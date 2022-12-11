from drf_yasg import openapi
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema

from .serializers.project_serializers import ProjectSerializer
from .serializers.card_serializers import CardSerializer, CardUpdateSerializer, CardMarkSerializer, \
    CardMarkDetailSerializer, CardFileSerializer, CardFileDetailSerializer, CardCommentSerializer, \
    CardCommentDetailSerializer, CardCommentUpdateSerializer
from .serializers.column_serializers import BarSerializer
from .serializers.board_serializers import BoardSerializer, BoardUpdateSerializer, BoardPatchSerializer, \
    BoardDetailSerializer, BoardFavouriteSerializer, BoardMemberSerializer, BoardMarkSerializer, \
    BoardMarkUpdateSerializer, BoardsLastSeenSerializer
from .permissions import IsProjectOwnerOrReadOnly, IsBoardOwnerOrMember, IsBoardMember, IsCommentOwner
from boards.models import (Project, Board, Column,
                           Card, Mark, CardMark, CardFile, CardComment,
                           BoardMember, BoardLastSeen, BoardFavourite)


class ProjectView(APIView):

    @swagger_auto_schema(responses={200: ProjectSerializer(many=True)},
                         operation_summary='Reads all Projects that current user owns')
    def get(self, request):
        self.check_permissions(request)

        projects = Project.objects.filter(owner=request.user)
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(operation_summary='Creates a new Project for current user',
                         request_body=ProjectSerializer)
    def post(self, request):
        self.check_permissions(request)

        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=self.request.user)
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class ProjectDetailView(APIView):
    permission_classes = (IsProjectOwnerOrReadOnly,)

    @swagger_auto_schema(responses={200: ProjectSerializer()},
                         operation_summary='Reads certain Project by pk')
    def get(self, request, pk):
        project = Project.objects.get(pk=pk)
        self.check_object_permissions(request, project)

        serializer = ProjectSerializer(project)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=ProjectSerializer, operation_summary='Updates certain Project by pk')
    def put(self, request, pk):
        project = Project.objects.get(pk=pk)
        self.check_object_permissions(request, project)

        serializer = ProjectSerializer(project, data=request.data)
        if serializer.is_valid():
            serializer.save(owner=self.request.user)
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(serializer.data, status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_summary='Deletes a certain Project by pk')
    def delete(self, request, pk):
        project = Project.objects.get(pk=pk)
        self.check_object_permissions(request, project)
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BoardView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    is_archived = openapi.Parameter('is_archived', openapi.IN_QUERY,
                                    description="Set True, t or 1 to sort out archived boards. "
                                                "False, f or 0 otherwise",
                                    type=openapi.TYPE_STRING)

    def get_queryset(self, request):
        self.check_permissions(request)

        boards = BoardMember.objects.filter(user=request.user)
        is_archived = request.query_params.get('is_archived', False)

        if is_archived is not None:
            boards = boards.filter(board__is_archived=is_archived)

        return [board.board for board in boards]

    @swagger_auto_schema(responses={200: BoardSerializer(many=True)},
                         operation_summary='Reads all Boards that the current user is member of',
                         manual_parameters=(is_archived,))
    def get(self, request):
        boards = self.get_queryset(request=request)
        serializer = BoardSerializer(boards, many=True)
        return Response(serializer.data)


class ProjectBoardView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = (IsProjectOwnerOrReadOnly,)

    def get_object(self):
        return Project.objects.get(pk=self.kwargs['pk'])

    @swagger_auto_schema(responses={200: BoardSerializer(many=True)},
                         operation_summary='Reads all Boards that were created under a certain Project')
    def get(self, request, pk):
        project = self.get_object()
        boards = project.boards
        self.check_object_permissions(request, project)
        serializer = BoardSerializer(boards, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=BoardSerializer, operation_summary='Creates a new Board under a certain Project')
    def post(self, request, pk):
        project = self.get_object()
        self.check_object_permissions(request, project)
        serializer = BoardSerializer(data=request.data)

        if serializer.is_valid():
            instance = serializer.save(project=self.kwargs['pk'])
            BoardMember.objects.create(user=request.user, board=instance)
            BoardLastSeen.objects.create(user=request.user, board=instance)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BoardDetailView(APIView):
    permission_classes = (IsBoardOwnerOrMember,)

    @swagger_auto_schema(responses={200: BoardDetailSerializer()},
                         operation_summary='Reads a certain Board by pk')
    def get(self, request, pk):
        board = Board.objects.get(pk=pk)
        self.check_object_permissions(request, board)
        serializer = BoardDetailSerializer(board)
        recent, created = BoardLastSeen.objects.get_or_create(user=request.user, board=board)
        recent.save()
        return Response(serializer.data)

    @swagger_auto_schema(request_body=BoardUpdateSerializer, operation_summary='Updates a Board by pk')
    def put(self, request, pk):
        board = Board.objects.get(pk=pk)
        self.check_object_permissions(request, board)
        serializer = BoardDetailSerializer(board, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=BoardPatchSerializer, operation_summary='Partially updates a Board by pk')
    def patch(self, request, pk):
        board = Board.objects.get(pk=pk)
        self.check_object_permissions(request, board)
        serializer = BoardSerializer(board, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_summary='Deletes a certain Board by pk')
    def delete(self, request, pk):
        board = Board.objects.get(pk=pk)
        self.check_object_permissions(request, board)
        board.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BoardsFavouriteView(APIView):
    permission_classes = (IsBoardMember,)

    @swagger_auto_schema(responses={200: BoardFavouriteSerializer(many=True)},
                         operation_summary='Reads current user\'s Favourite Boards')
    def get(self, request):
        self.check_permissions(request)
        boards = [b.board for b in BoardFavourite.objects.filter(user=request.user)]
        serializer = BoardSerializer(boards, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=BoardFavouriteSerializer,
                         operation_summary='Makes a certain Board user\'s Favourite')
    def post(self, request):
        self.check_permissions(request)

        serializer = BoardFavouriteSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save(user=request.user)

        return Response({'Details': 'Board was successfully added to Favourites'},
                        status=status.HTTP_201_CREATED)

    @swagger_auto_schema(request_body=BoardFavouriteSerializer,
                         operation_summary='Removes boards from Favourites')
    def delete(self, request):

        delete_ids = [b['board'] for b in request.data]
        favourites = BoardFavourite.objects.filter(board__in=delete_ids)
        favourites.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BoardsLastSeenView(APIView):

    @swagger_auto_schema(responses={200: BoardsLastSeenSerializer(many=True)},
                         operation_summary='Reads all user\'s Last Seen Boards')
    def get(self, request):
        self.check_permissions(request)

        boards = BoardLastSeen.objects.filter(user=request.user).order_by('-timestamp')
        serializer = BoardsLastSeenSerializer(boards, many=True)
        return Response(serializer.data)


class BoardMemberAddView(APIView):
    permission_classes = (IsBoardOwnerOrMember,)

    @swagger_auto_schema(request_body=BoardMemberSerializer,
                         operation_summary='Adds a member to a certain Board')
    def post(self, request, pk):
        board = Board.objects.get(pk=pk)
        self.check_object_permissions(request, board)

        serializer = BoardMemberSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(board=pk)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ColumnView(APIView):
    permission_classes = (IsBoardMember, )

    @swagger_auto_schema(request_body=BarSerializer,
                         operation_summary='Creates a new Column Object')
    def post(self, request, pk):
        board = Board.objects.get(pk=pk)
        self.check_object_permissions(request, board)

        serializer = BarSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(board=pk)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ColumnDetailView(APIView):
    permission_classes = (IsBoardMember, )

    @swagger_auto_schema(responses={200: BarSerializer()},
                         operation_summary='Read a certain Column Object')
    def get(self, request, pk):
        column = Column.objects.get(pk=pk)
        self.check_object_permissions(request, column.board)
        serializer = BarSerializer(column)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=BarSerializer, operation_summary='Updates a new Column Object')
    def put(self, request, pk):
        column = Column.objects.get(pk=pk)
        self.check_object_permissions(request, column.board)
        serializer = BarSerializer(column, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_summary='Delete a certain Column Object')
    def delete(self, request, pk):
        column = Column.objects.get(pk=pk)
        self.check_object_permissions(request, column.board)
        column.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CardView(APIView):
    permission_classes = (IsBoardMember, )

    @swagger_auto_schema(request_body=CardSerializer,
                         operation_summary='Creates a new Card Object')
    def post(self, request, pk):
        column = Column.objects.get(pk=pk)
        self.check_object_permissions(request, column.board)
        serializer = CardSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(column=pk)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CardDetailView(APIView):
    permission_classes = (IsBoardMember, )

    @swagger_auto_schema(responses={200: CardSerializer()},
                         operation_summary='Read a certain Card Object')
    def get(self, request, pk):
        card = Card.objects.get(pk=pk)
        self.check_object_permissions(request, card.column.board)

        serializer = CardSerializer(card)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=CardSerializer, operation_summary='Updates a new Card Object')
    def put(self, request, pk):
        card = Card.objects.get(pk=pk)
        self.check_object_permissions(request, card.column.board)
        serializer = CardSerializer(card, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=CardUpdateSerializer, operation_summary='Updates a new Card partially by pk')
    def patch(self, request, pk):
        card = Card.objects.get(pk=pk)
        self.check_object_permissions(request, card.column.board)

        serializer = CardSerializer(card, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_summary='Delete a certain Card Object')
    def delete(self, request, pk):
        card = Card.objects.get(pk=pk)
        self.check_object_permissions(request, card.column.board)
        card.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BoardMarkView(APIView):
    permission_classes = (IsBoardMember, )

    @swagger_auto_schema(responses={200: BoardMarkSerializer(many=True)},
                         operation_summary='Read all Card Label Objects')
    def get(self, request, pk):
        board = Board.objects.get(pk=pk)
        self.check_object_permissions(request, board)

        marks = Mark.objects.filter(board=board)
        serializer = BoardMarkSerializer(marks, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=BoardMarkSerializer, operation_summary='Creates a new Card Label Object')
    def post(self, request, pk):
        board = Board.objects.get(pk=pk)
        self.check_object_permissions(request, board)

        serializer = BoardMarkSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(board=pk)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BoardMarkDetailView(APIView):
    permission_classes = (IsBoardMember, )

    @swagger_auto_schema(responses={200: BoardMarkSerializer()},
                         operation_summary='Read a certain Card Label Object')
    def get(self, request, pk):
        board_mark = Mark.objects.get(pk=pk)
        self.check_object_permissions(request, board_mark.board)

        serializer = BoardMarkSerializer(board_mark)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=BoardMarkSerializer,
                         operation_summary='Updates a certain Mark by pk')
    def put(self, request, pk):
        board_mark = Mark.objects.get(pk=pk)
        self.check_object_permissions(request, board_mark.board)

        serializer = BoardMarkSerializer(board_mark, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=BoardMarkUpdateSerializer,
                         operation_summary='Partially updates a certain Mark by pk')
    def patch(self, request, pk):
        board_mark = Mark.objects.get(pk=pk)
        self.check_object_permissions(request, board_mark.board)

        serializer = BoardMarkSerializer(board_mark, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_summary='Deletes a certain Board Mark by pk')
    def delete(self, request, pk):
        board_mark = Mark.objects.get(pk=pk)
        self.check_object_permissions(request, board_mark.board)

        board_mark.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CardMarkView(APIView):
    permission_classes = (IsBoardMember, )

    @swagger_auto_schema(request_body=CardMarkSerializer,
                         operation_summary='Adding Mark to a Card')
    def post(self, request, pk):
        card = Card.objects.get(pk=pk)
        self.check_object_permissions(request, card.column.board)

        serializer = CardMarkSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(card=pk)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CardMarkDetailView(APIView):
    permission_classes = (IsBoardMember, )

    @swagger_auto_schema(request_body=CardMarkDetailSerializer,
                         operation_summary='Deletes marks(s) from a certain card')
    def delete(self, request, pk):
        card = Card.objects.get(pk=pk)
        delete_ids = [b['mark'] for b in request.data]
        card_marks = CardMark.objects.filter(mark__in=delete_ids, card=card)
        card_marks.delete()
        self.check_object_permissions(request, card.column.board)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CardFileView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = (IsBoardMember, )

    @swagger_auto_schema(responses={200: CardFileSerializer(many=True)},
                         operation_summary='Reads all Files uploaded to a certain Card')
    def get(self, request, pk):
        card = Card.objects.get(pk=pk)
        self.check_object_permissions(request, card.column.board)

        files = CardFile.objects.filter(card=card)
        serializer = CardFileSerializer(files, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=CardFileSerializer, operation_summary='Uploads new File to a certain Card')
    def post(self, request, pk):
        card = Card.objects.get(pk=pk)
        self.check_object_permissions(request, card.column.board)

        serializer = CardFileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(card=pk)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CardFileDetailView(APIView):
    permission_classes = (IsBoardMember,)

    @swagger_auto_schema(request_body=CardFileDetailSerializer,
                         operation_summary='Deletes a certain Card File by pk')
    def delete(self, request, pk):
        card = Card.objects.get(pk=pk)
        self.check_object_permissions(request, card.column.board)

        delete_ids = [b['file'] for b in request.data]
        card_files = CardFile.objects.filter(id__in=delete_ids, card=card)
        card_files.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class CardCommentView(APIView):
    permission_classes = (IsBoardMember, )

    @swagger_auto_schema(responses={200: CardCommentSerializer(many=True)},
                         operation_summary='Read all Card Comments')
    def get(self, request, pk):
        card = Card.objects.get(pk=pk)
        self.check_object_permissions(request, card.column.board)

        comments = CardComment.objects.filter(card=card)
        serializer = CardCommentSerializer(comments)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=CardCommentSerializer, operation_summary='Creates a new Comment to a certain Card')
    def post(self, request, pk):
        card = Card.objects.get(pk=pk)
        self.check_object_permissions(request, card.column.board)

        serializer = CardCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, card=pk)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=CardCommentDetailSerializer,
                         operation_summary='Deletes a certain Card Comment by pk')
    def delete(self, request, pk):
        card = Card.objects.get(pk=pk)
        self.check_object_permissions(request, card.column.board)

        delete_ids = [b['id'] for b in request.data]
        comments = CardComment.objects.filter(id__in=delete_ids)
        comments.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class CardCommentDetailView(APIView):
    permission_classes = (IsCommentOwner, )

    @swagger_auto_schema(request_body=CardCommentUpdateSerializer,
                         operation_summary='Updates a new Comment to a certain Card')
    def put(self, request, pk):
        card_comment = CardComment.objects.get(pk=pk)
        self.check_object_permissions(request, card_comment)

        serializer = CardCommentSerializer(card_comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


