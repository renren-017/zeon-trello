from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema

from .serializers import BoardSerializer, BarSerializer, CardSerializer, CardLabelSerializer, \
    CardFileSerializer, CardCommentSerializer, CardChecklistItemSerializer
from boards.models import Board, Bar, Card, CardLabel, CardFile, CardComment, CardChecklistItem


class BoardView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(operation_summary='Reads all Board Objects')
    def get(self, request):
        boards = Board.objects.filter(members__in=[request.user])
        serializer = BoardSerializer(boards, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=BoardSerializer, operation_summary='Creates a new Board Object')
    def post(self, request):
        serializer = BoardSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BoardDetailView(APIView):
    @swagger_auto_schema(operation_summary='Read a certain Board Object')
    def get(self, request, pk):
        board = Board.objects.get(members__in=[request.user], pk=pk)
        serializer = BoardSerializer(board)
        return Response(serializer.data)


class BarView(APIView):
    @swagger_auto_schema(operation_summary='Read all Bar Objects')
    def get(self, request, pk):
        board = Board.objects.get(pk=pk)
        bars = Bar.objects.filter(board=board)
        serializer = BarSerializer(bars, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=BarSerializer, operation_summary='Creates a new Bar Object')
    def post(self, request, pk):
        serializer = BarSerializer(data=request.data)
        if serializer.is_valid():
            board = Board.objects.get(pk=pk)
            serializer.save(board=board)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class CardView(APIView):
    @swagger_auto_schema(operation_summary='Read all Bar Objects')
    def get(self, request):
        bars = Card.objects.filter(members__in=[request.user])
        serializer = BarSerializer(bars)
        return Response(serializer.data)


class CardLabelView(APIView):
    @swagger_auto_schema(operation_summary='Read all Bar Objects')
    def get(self, request, pk):
        bars = Bar.objects.filter(board=pk)
        serializer = BarSerializer(bars)
        return Response(serializer.data)


class CardFileView(APIView):
    @swagger_auto_schema(operation_summary='Read all Bar Objects')
    def get(self, request):
        bars = Bar.objects.filter(members__in=[request.user])
        serializer = BarSerializer(bars)
        return Response(serializer.data)