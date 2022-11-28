from rest_framework import serializers
from boards.models import Board, Bar, Card, CardLabel, CardComment, CardFile, CardChecklistItem


class BoardSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(max_length=50)
    background_img = serializers.ImageField()
    is_starred = serializers.BooleanField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)

    created_on = serializers.DateTimeField(read_only=True)
    last_modified = serializers.DateTimeField(read_only=True)

    members = serializers.StringRelatedField(many=True, read_only=True)

    def create(self, validated_data):
        board = Board(title=validated_data['title'],
                      background_img=validated_data['background_img'])
        board.members.add(self.request.user)
        board.save()
        return board


class BarSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    board = serializers.IntegerField(read_only=True)
    title = serializers.CharField(max_length=30)

    def create(self, validated_data):
        return Bar(**validated_data).save()


class CardSerializer(serializers.Serializer):

    def create(self, validated_data):
        return Card(**validated_data).save()


class CardLabelSerializer(serializers.Serializer):
    def create(self, validated_data):
        return CardLabel(**validated_data).save()


class CardFileSerializer(serializers.Serializer):

    def create(self, validated_data):
        return CardFile(**validated_data).save()


class CardCommentSerializer(serializers.Serializer):

    def create(self, validated_data):
        return CardComment(**validated_data).save()


class CardChecklistItemSerializer(serializers.Serializer):

    def create(self, validated_data):
        return CardChecklistItem(**validated_data).save()