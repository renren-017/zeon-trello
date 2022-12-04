from drf_yasg import openapi
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema

from .serializers import (BoardSerializer, BoardDetailSerializer, BoardFavouriteSerializer, BoardsLastSeenSerializer,
                          BarSerializer,
                          CardSerializer,
                          CardLabelSerializer,
                          CardFileSerializer,
                          CardCommentSerializer,
                          CardChecklistItemSerializer,
                          ProjectSerializer, BoardUpdateSerializer, BoardMemberSerializer, )
from .permissions import IsProjectOwnerOrReadOnly, IsBoardOwnerOrMember, IsBoardMember
from boards.models import (Board, Column,
                           Card, Mark, CardFile, CardComment,
                           Project,
                           BoardMember, BoardLastSeen, BoardFavourite)


class ProjectView(APIView):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(operation_summary='Reads all Projects that current user owns')
    def get(self, request):
        self.check_permissions(request)

        projects = Project.objects.filter(owner=request.user)
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(operation_summary='Creates a new Project for current user', request_body=ProjectSerializer)
    def post(self, request):
        self.check_permissions(request)

        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=self.request.user)
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class ProjectDetailView(APIView):
    permission_classes = (IsProjectOwnerOrReadOnly,)

    @swagger_auto_schema(operation_summary='Reads certain Project by pk')
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
    permission_classes = (IsAuthenticated,)

    is_archived = openapi.Parameter('is_archived', openapi.IN_QUERY,
                                    description="Set True, t or 1 to sort out archived boards. "
                                                "False, f or 0 otherwise",
                                    type=openapi.TYPE_STRING)

    def get_queryset(self, request):
        boards = BoardMember.objects.filter(user=request.user)
        is_archived = self.request.query_params.get('is_archived', False)

        if is_archived is not None:
            boards = boards.filter(board__is_archived=is_archived)

        return [board.board for board in boards]

    @swagger_auto_schema(operation_summary='Reads all Boards that the current user is member of',
                         manual_parameters=(is_archived,))
    def get(self, request):
        self.check_permissions(request)
        boards = self.get_queryset(request)
        serializer = BoardSerializer(boards, many=True)
        return Response(serializer.data)


class ProjectBoardView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = (IsProjectOwnerOrReadOnly,)

    def get_object(self):
        return Project.objects.get(pk=self.kwargs['pk'])

    @swagger_auto_schema(operation_summary='Reads all Boards that were created under a certain Project')
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

    @swagger_auto_schema(operation_summary='Reads a certain Board by pk')
    def get(self, request, pk):
        board = Board.objects.get(pk=pk)
        self.check_object_permissions(request, board)
        serializer = BoardDetailSerializer(board)
        recent, created = BoardLastSeen.objects.get_or_create(user=request.user, board=board)
        recent.save()
        return Response(serializer.data)

    @swagger_auto_schema(request_body=BoardSerializer, operation_summary='Updates a Board by pk')
    def put(self, request, pk):
        board = Board.objects.get(pk=pk)
        self.check_object_permissions(request, board)
        serializer = BoardDetailSerializer(board, data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            BoardLastSeen(user=request.user, board=instance).save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=BoardUpdateSerializer, operation_summary='Partially updates a Board by pk')
    def patch(self, request, pk):
        board = Board.objects.get(pk=pk)
        self.check_object_permissions(request, board)
        serializer = BoardSerializer(board, data=request.data, partial=True)
        if serializer.is_valid():
            instance = serializer.save()
            BoardLastSeen(user=request.user, board=instance).save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_summary='Deletes a certain Board by pk')
    def delete(self, request, pk):
        board = Board.objects.get(pk=pk)
        self.check_object_permissions(request, board)
        board.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BoardsFavouriteView(APIView):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(operation_summary='Reads current user\'s Favourite Boards')
    def get(self, request):
        self.check_permissions(request)
        boards = [b.board for b in BoardFavourite.objects.filter(user=request.user)]
        serializer = BoardSerializer(boards, many=True)
        return Response(serializer.data)


class BoardsFavouriteDetailView(APIView):
    permission_classes = (IsBoardMember,)

    @swagger_auto_schema(operation_summary='Makes a certain Board user\'s Favourite')
    def get(self, request, pk):
        board = Board.objects.get(pk=pk)
        self.check_object_permissions(request, board)
        BoardFavourite.objects.create(user=request.user, board=board)
        return Response({'Details': 'Board was successfully added to Favourites'},
                        status=status.HTTP_201_CREATED)


class BoardsLastSeenView(APIView):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(operation_summary='Reads all user\'s Last Seen Boards')
    def get(self, request):
        self.check_permissions(request)
        boards = BoardLastSeen.objects.filter(user=request.user).order_by('-timestamp')
        serializer = BoardsLastSeenSerializer(boards, many=True)
        return Response(serializer.data)


class BoardMemberAddView(APIView):
    permission_classes = (IsBoardOwnerOrMember,)

    @swagger_auto_schema(request_body=BoardMemberSerializer, operation_summary='Adds a member to a certain Board')
    def post(self, request, pk):
        board = Board.objects.get(pk=pk)
        self.check_object_permissions(request, board)

        serializer = BoardMemberSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(board=pk)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BarView(APIView):
    permission_classes = (IsBoardMember, )

    # @swagger_auto_schema(operation_summary='Read all Column Objects')
    # def get(self, request, pk):
    #     board = Board.objects.get(pk=pk)
    #     self.check_object_permissions(request, board)
    #     bars = Column.objects.filter(board=board)
    #     serializer = BarSerializer(bars, many=True)
    #     return Response(serializer.data)

    @swagger_auto_schema(request_body=BarSerializer, operation_summary='Creates a new Column Object')
    def post(self, request, pk):
        board = Board.objects.get(pk=pk)
        self.check_object_permissions(request, board)

        serializer = BarSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(board=pk)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BarDetailView(APIView):
    permission_classes = (IsBoardMember, )


    @swagger_auto_schema(operation_summary='Read a certain Column Object')
    def get(self, request, pk):
        bar = Column.objects.get(pk=pk)
        self.check_object_permissions(request, bar.board)
        serializer = BarSerializer(bar)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=BarSerializer, operation_summary='Updates a new Column Object')
    def put(self, request, pk):
        bar = Column.objects.get(pk=pk)
        self.check_object_permissions(request, bar.board)
        serializer = BarSerializer(bar, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_summary='Delete a certain Column Object')
    def delete(self, request, pk):
        bar = Column.objects.get(pk=pk)
        self.check_object_permissions(request, bar.board)
        bar.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CardView(APIView):
    @swagger_auto_schema(operation_summary='Read all Card Objects')
    def get(self, request):
        cards = Card.objects.all()
        serializer = CardSerializer(cards)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=CardSerializer, operation_summary='Creates a new Card Object')
    def post(self, request):
        serializer = CardSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CardDetailView(APIView):
    @swagger_auto_schema(operation_summary='Read a certain Card Object')
    def get(self, request, pk):
        card = Card.objects.get(pk=pk)
        serializer = CardSerializer(card)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=CardSerializer, operation_summary='Updates a new Card Object')
    def put(self, request, pk):
        card = Card.objects.get(pk=pk)
        serializer = CardSerializer(card, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_summary='Delete a certain Card Object')
    def delete(self, request, pk):
        card = Card.objects.get(pk=pk)
        card.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CardLabelView(APIView):

    @swagger_auto_schema(operation_summary='Read all Card Label Objects')
    def get(self, request, pk):
        labels = Mark.objects.all()
        serializer = CardLabelSerializer(labels)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=CardLabelSerializer, operation_summary='Creates a new Card Label Object')
    def post(self, request):
        serializer = CardLabelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CardLabelDetailView(APIView):
    @swagger_auto_schema(operation_summary='Read a certain Card Label Object')
    def get(self, request, pk):
        card_label = Mark.objects.get(pk=pk)
        serializer = CardLabelSerializer(card_label)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=CardLabelSerializer, operation_summary='Updates a new Card Label Object')
    def put(self, request, pk):
        card_label = Mark.objects.get(pk=pk)
        serializer = CardLabelSerializer(card_label, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_summary='Delete a certain Card Label Object')
    def delete(self, request, pk):
        card_label = Mark.objects.get(pk=pk)
        card_label.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CardFileView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(operation_summary='Read all Card Label Objects')
    def get(self, request, pk):
        files = CardFile.objects.all()
        serializer = CardFileSerializer(files)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=CardFileSerializer, operation_summary='Creates a new Card File Object')
    def post(self, request):
        serializer = CardFileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CardFileDetailView(APIView):
    @swagger_auto_schema(operation_summary='Read a certain Card File Object')
    def get(self, request, pk):
        card_file = CardFile.objects.get(pk=pk)
        serializer = CardFileSerializer(card_file)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=CardFileSerializer, operation_summary='Updates a new Card File Object')
    def put(self, request, pk):
        card_file = CardFile.objects.get(pk=pk)
        serializer = CardFileSerializer(card_file, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_summary='Delete a certain Card Label Object')
    def delete(self, request, pk):
        card_file = CardFile.objects.get(pk=pk)
        card_file.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CardCommentView(APIView):

    @swagger_auto_schema(operation_summary='Read all Card Comment Objects')
    def get(self, request, pk):
        comments = CardComment.objects.all()
        serializer = CardCommentSerializer(comments)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=CardCommentSerializer, operation_summary='Creates a new Card Comment Object')
    def post(self, request):
        serializer = CardCommentSerializer(data=request.data)
        if serializer.is_valid():
            card_comment = serializer.save()
            card_comment.user = self.request.user
            card_comment.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


