from drf_yasg import openapi
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema

from .serializers import BoardSerializer, BarSerializer, CardSerializer, CardLabelSerializer, \
    CardFileSerializer, CardCommentSerializer, CardChecklistItemSerializer
from boards.models import Board, Bar, Card, CardLabel, CardFile, CardComment, CardChecklistItem

response_schema_dict = {
    "200": openapi.Response(
        description="Successful request response",
        examples={
            "application/json":{
                  "id": 18,
                  "title": "Example Board",
                  "background_img": "https://zeon-trello-bucket.s3.amazonaws.com/back_img/back_img/back_img/back_img/flat-80s-party-instagram-stories-collection_23-2149432631.webp?AWSAccessKeyId=AKIA5LYIWSFGCMJYHBAF&Signature=JcR4vO53fSWcQlEAyhiR%2FBA8V88%3D&Expires=1669710349",
                  "is_starred": False,
                  "is_active": True,
                  "created_on": "2022-11-28T11:41:32.589304Z",
                  "last_modified": "2022-11-29T07:25:23.683824Z",
                  "members": [
                    "rene@gmail.com",
                    "altynai.mamytova@alatoo.edu.kg"
                  ],
                  "bars": [
                    {
                      "id": 14,
                      "board": "Example Board",
                      "title": "Example Bar",
                      "cards": []
                    }
                  ]
            }
        }
    )
}


class BoardView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(responses=response_schema_dict, operation_summary='Reads all Board Objects')
    def get(self, request):
        boards = Board.objects.filter(members__in=[request.user])
        serializer = BoardSerializer(boards, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=BoardSerializer, operation_summary='Creates a new Board Object')
    def post(self, request):
        serializer = BoardSerializer(data=request.data)
        if serializer.is_valid():
            board_instance = serializer.save()
            board_instance.members.add(request.user.pk)
            board_instance.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BoardDetailView(APIView):
    @swagger_auto_schema(operation_summary='Read a certain Board Object')
    def get(self, request, pk):
        board = Board.objects.get(members__in=[request.user], pk=pk)
        serializer = BoardSerializer(board)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=BoardSerializer, operation_summary='Updates a new Board Object')
    def put(self, request, pk):
        board = Board.objects.get(pk=pk)
        serializer = BoardSerializer(board, data=request.data)
        if serializer.is_valid():
            board_instance = serializer.save()
            board_instance.members.add(request.user.pk)
            board_instance.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_summary='Delete a certain Board Object')
    def delete(self, request, pk):
        board = Board.objects.get(members__in=[request.user], pk=pk)
        board.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class StarredBoardsView(APIView):

    @swagger_auto_schema(operation_summary='Reads all Board Objects')
    def get(self, request):
        boards = Board.objects.filter(members__in=[request.user], is_starred=True)
        serializer = BoardSerializer(boards, many=True)
        return Response(serializer.data)


class BarView(APIView):

    @swagger_auto_schema(operation_summary='Read all Bar Objects')
    def get(self, request):
        bars = Bar.objects.all()
        serializer = BarSerializer(bars, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=BarSerializer, operation_summary='Creates a new Bar Object')
    def post(self, request):
        serializer = BarSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BarDetailView(APIView):

    @swagger_auto_schema(operation_summary='Read a certain Bar Object')
    def get(self, request, pk):
        bar = Bar.objects.get(pk=pk)
        serializer = BarSerializer(bar)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=BarSerializer, operation_summary='Updates a new Bar Object')
    def put(self, request, pk):
        bar = Bar.objects.get(pk=pk)
        serializer = BarSerializer(bar, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_summary='Delete a certain Bar Object')
    def delete(self, request, pk):
        bar = Bar.objects.get(pk=pk)
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
        labels = CardLabel.objects.all()
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
        card_label = CardLabel.objects.get(pk=pk)
        serializer = CardLabelSerializer(card_label)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=CardLabelSerializer, operation_summary='Updates a new Card Label Object')
    def put(self, request, pk):
        card_label = CardLabel.objects.get(pk=pk)
        serializer = CardLabelSerializer(card_label, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_summary='Delete a certain Card Label Object')
    def delete(self, request, pk):
        card_label = CardLabel.objects.get(pk=pk)
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
