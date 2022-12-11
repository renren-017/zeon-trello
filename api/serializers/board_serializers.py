from collections import OrderedDict
from io import BytesIO

from PIL import Image
from django.core.files import File
from rest_framework import serializers

from api.serializers.user_serializers import User, UserSerializer
from api.serializers.column_serializers import BarSerializer
from boards.models import Project, Board, BoardMember, BoardFavourite, Mark


def compress_img(image_to_compress):
    image = Image.open(image_to_compress)
    image_output = BytesIO()
    image.save(image_output,
               "JPEG",
               optimize=True,
               quality=30)
    image = File(image_output, name=image_to_compress.name)
    return image


class BoardSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    project = serializers.PrimaryKeyRelatedField(read_only=True)
    title = serializers.CharField(max_length=50)
    background_img = serializers.ImageField()
    is_archived = serializers.BooleanField(read_only=True)

    created_on = serializers.DateTimeField(read_only=True)
    last_modified = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        background_img = compress_img(validated_data['background_img'])
        project = Project.objects.get(pk=validated_data['project'])

        board = Board(title=validated_data['title'],
                      project=project,
                      background_img=background_img)
        board.save()

        return board

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        if validated_data.get('background_img'):
            instance.background_img = compress_img(validated_data['background_img'])
        instance.save()
        return instance


class BoardUpdateSerializer(BoardSerializer):
    # Only for schema generation, not actually used.
    # because DRF-YASG does not support partial.
    def get_fields(self):
        new_fields = super().get_fields()
        new_fields['is_archived'] = serializers.BooleanField()
        return new_fields


class BoardPatchSerializer(BoardSerializer):
    # Only for schema generation, not actually used.
    # because DRF-YASG does not support partial.
    def get_fields(self):
        new_fields = OrderedDict()
        for name, field in super().get_fields().items():
            field.required = False
            new_fields[name] = field
        new_fields['is_archived'] = serializers.BooleanField()
        new_fields['is_archived'].required = False
        return new_fields


class BoardDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    project = serializers.PrimaryKeyRelatedField(read_only=True)
    title = serializers.CharField(max_length=50, required=False)
    background_img = serializers.ImageField(required=False)

    created_on = serializers.DateTimeField(read_only=True)
    last_modified = serializers.DateTimeField(read_only=True)

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        if validated_data.get('background_img'):
            instance.background_img = compress_img(validated_data['background_img'])
        instance.save()
        return instance

    def to_representation(self, instance):
        members = [member.user for member in BoardMember.objects.filter(board=instance)]
        representation = super().to_representation(instance)
        representation['columns'] = BarSerializer(instance.columns.all(), many=True, context=self.context).data
        representation['members'] = UserSerializer(members, many=True, context=self.context).data
        return representation


class BoardFavouriteSerializer(serializers.Serializer):
    board = serializers.IntegerField()
    user = serializers.IntegerField(read_only=True)

    def create(self, validated_data):
        board = Board.objects.get(pk=validated_data['board'])
        bf, created = BoardFavourite(
            board=board,
            user=validated_data['user']
        )
        bf.save()
        return bf


class BoardMemberSerializer(serializers.Serializer):
    board = serializers.PrimaryKeyRelatedField(read_only=True)
    user = serializers.EmailField()

    def create(self, validated_data):
        board_member = BoardMember(
            board=Board.objects.get(pk=validated_data['board']),
            user=User.objects.get(email=validated_data['user'])
        )
        board_member.save()

        return board_member


class BoardMarkSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    board = serializers.PrimaryKeyRelatedField(read_only=True)
    title = serializers.CharField(max_length=30)
    color = serializers.CharField(default='#000', max_length=7)

    def create(self, validated_data):
        board = Board.objects.get(pk=validated_data['board'])
        mark = Mark(
            board=board,
            title=validated_data['title'],
            color=validated_data['color']
        )
        mark.save()
        return mark

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.color = validated_data.get('color', instance.color)
        instance.save()
        return instance


class BoardMarkUpdateSerializer(BoardMarkSerializer):
    # Only for schema generation, not actually used.
    # because DRF-YASG does not support partial.
    def get_fields(self):
        new_fields = OrderedDict()
        for name, field in super().get_fields().items():
            field.required = False
            new_fields[name] = field
        return new_fields


class BoardsLastSeenSerializer(serializers.Serializer):
    timestamp = serializers.DateTimeField(read_only=True)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['board'] = BoardSerializer(instance.board, context=self.context).data
        return representation
