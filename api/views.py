from drf_yasg import openapi
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema

from .serializers import BoardSerializer, BarSerializer, CardSerializer, CardLabelSerializer, \
    CardFileSerializer, CardCommentSerializer, CardChecklistItemSerializer, ProjectSerializer, BoardDetailSerializer, \
    BoardFavouriteSerializer
from .permissions import OwnerOrReadOnly, IsBoardOwnerOrMember, IsBoardMember
from boards.models import Board, Column, Card, Mark, CardFile, CardComment, Project, BoardMember, BoardLastSeen, \
    BoardFavourite


class ProjectView(APIView):
    permission_classes = (OwnerOrReadOnly,)

    @swagger_auto_schema(operation_summary='Reads all Project Objects')
    def get(self, request):
        self.check_permissions(request)

        projects = Project.objects.all()
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(operation_summary='Creates new Project Object', request_body=ProjectSerializer)
    def post(self, request):
        self.check_permissions(request)

        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=self.request.user)
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class ProjectDetailView(APIView):
    permission_classes = (OwnerOrReadOnly,)

    @swagger_auto_schema(operation_summary='Reads certain Project')
    def get(self, request, pk):
        project = Project.objects.get(pk=pk)
        self.check_object_permissions(request, project)

        serializer = ProjectSerializer(project)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=ProjectSerializer, operation_summary='Updates certain Project Object')
    def put(self, request, pk):
        project = Project.objects.get(pk=pk)
        self.check_object_permissions(request, project)

        serializer = ProjectSerializer(project, data=request.data)
        if serializer.is_valid():
            serializer.save(owner=self.request.user)
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(serializer.data, status.HTTP_400_BAD_REQUEST)


class BoardView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(operation_summary='Reads all Board Objects')
    def get(self, request):
        self.check_permissions(request)

        boards = [bm.board for bm in BoardMember.objects.filter(member=request.user)]
        serializer = BoardSerializer(boards, many=True)
        return Response(serializer.data)


class ProjectBoardView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = (OwnerOrReadOnly,)

    def get_object(self):
        return Project.objects.get(pk=self.kwargs['pk'])

    @swagger_auto_schema(operation_summary='Reads all Board Objects')
    def get(self, request, pk):
        project = self.get_object()
        boards = project.boards
        self.check_object_permissions(request, project)
        serializer = BoardSerializer(boards, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=BoardSerializer, operation_summary='Creates a new Board Object')
    def post(self, request, pk):
        project = self.get_object()
        self.check_object_permissions(request, project)
        serializer = BoardSerializer(data=request.data)

        if serializer.is_valid():
            instance = serializer.save(project=self.kwargs['pk'])
            BoardMember.objects.create(member=request.user, board=instance)
            BoardLastSeen.objects.create(user=request.user, board=instance)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BoardDetailView(APIView):
    permission_classes = (IsBoardOwnerOrMember,)

    @swagger_auto_schema(operation_summary='Read a certain Board Object')
    def get(self, request, pk):
        board = Board.objects.get(pk=pk)
        self.check_object_permissions(request, board)
        serializer = BoardDetailSerializer(board)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=BoardSerializer, operation_summary='Updates a new Board Object')
    def put(self, request, pk):
        board = Board.objects.get(pk=pk)
        self.check_object_permissions(request, board)
        serializer = BoardDetailSerializer(board, data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            BoardLastSeen(user=request.user, board=instance).save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=BoardSerializer, operation_summary='Updates a new Board Object')
    def patch(self, request, pk):
        board = Board.objects.get(pk=pk)
        self.check_object_permissions(request, board)
        serializer = BoardSerializer(board, data=request.data, partial=True)
        if serializer.is_valid():
            instance = serializer.save()
            BoardLastSeen(user=request.user, board=instance).save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_summary='Delete a certain Board Object')
    def delete(self, request, pk):
        board = Board.objects.get(pk=pk)
        self.check_object_permissions(request, board)
        board.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BoardsFavouriteView(APIView):
    permission_classes = (IsBoardMember,)

    @swagger_auto_schema(request_body=BoardSerializer, operation_summary='Creates a new Board Object')
    def post(self, request, pk):
        board = Board.objects.get(pk=pk)
        self.check_object_permissions(request, board)
        serializer = BoardFavouriteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(board=board, user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(seri1alizer.errors, status=status.HTTP_400_BAD_REQUEST)


class BarView(APIView):

    @swagger_auto_schema(operation_summary='Read all Column Objects')
    def get(self, request):
        bars = Column.objects.all()
        serializer = BarSerializer(bars, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=BarSerializer, operation_summary='Creates a new Column Object')
    def post(self, request):
        serializer = BarSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BarDetailView(APIView):

    @swagger_auto_schema(operation_summary='Read a certain Column Object')
    def get(self, request, pk):
        bar = Column.objects.get(pk=pk)
        serializer = BarSerializer(bar)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=BarSerializer, operation_summary='Updates a new Column Object')
    def put(self, request, pk):
        bar = Column.objects.get(pk=pk)
        serializer = BarSerializer(bar, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_summary='Delete a certain Column Object')
    def delete(self, request, pk):
        bar = Column.objects.get(pk=pk)
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


class CardChecklistView(APIView):

    @swagger_auto_schema(operation_summary='Read all Card Checklist Objects')
    def get(self, request):
        checklist = CardChecklistItem.objects.all()
        serializer = CardChecklistItemSerializer(checklist)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=CardChecklistItemSerializer,
                         operation_summary='Creates a new Card Checklist Object')
    def post(self, request):
        serializer = CardChecklistItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
