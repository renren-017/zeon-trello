from collections import OrderedDict
from io import BytesIO
from PIL import Image
from django.core.files import File
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from boards.models import (Project, Board, Column, Card, Mark, CardComment, CardFile, BoardMember, BoardFavourite, CardMark)


User = get_user_model()


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    email = serializers.EmailField()


class BoardSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    project = serializers.PrimaryKeyRelatedField(read_only=True)
    title = serializers.CharField(max_length=50)
    background_img = serializers.ImageField()
    is_archived = serializers.BooleanField(read_only=True)

    created_on = serializers.DateTimeField(read_only=True)
    last_modified = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        background_img = validated_data['background_img']
        img = Image.open(background_img)
        img_output = BytesIO()
        img.save(img_output,
                 "JPEG",
                 optimize=True,
                 quality=30)
        background_img = File(img_output, name=background_img.name)
        project = Project.objects.get(pk=validated_data['project'])

        board = Board(title=validated_data['title'],
                      project=project,
                      background_img=background_img)
        board.save()

        return board

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.background_img = validated_data.get('background_img', instance.background_img)
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

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.background_img = validated_data.get('background_img', instance.background_img)
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


class BarSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(max_length=30)

    def create(self, validated_data):
        board = Board.objects.get(pk=validated_data['board'])
        column = Column(
            board=board,
            title=validated_data['title']
        )
        column.save()

        return column

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['cards'] = CardSerializer(instance.cards.all(), many=True, context=self.context).data
        return representation


class CardSerializer(serializers.Serializer):

    id = serializers.PrimaryKeyRelatedField(read_only=True)
    title = serializers.CharField(max_length=30)
    description = serializers.CharField(max_length=500)
    checklist = serializers.JSONField(default={'Make a to-do': False})
    deadline = serializers.DateTimeField()

    def create(self, validated_data):
        column = Column.objects.get(pk=validated_data['column'])
        card = Card(
            column=column,
            title=validated_data['title'],
            description=validated_data['description'],
            checklist=validated_data.get('checklist'),
            deadline=validated_data['deadline'],
        )

        card.save()
        return card

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        marks = [cardmark.mark for cardmark in instance.marks.all()]
        representation['marks'] = BoardMarkSerializer(marks, many=True, context=self.context).data
        representation['files'] = CardFileSerializer(instance.files.all(), many=True, context=self.context).data
        representation['comments'] = CardCommentSerializer(instance.comments.all(), many=True, context=self.context).data
        return representation

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.checklist = validated_data.get('checklist', instance.checklist)
        instance.deadline = validated_data.get('deadline', instance.deadline)
        instance.save()
        return instance


class CardUpdateSerializer(CardSerializer):
    # Only for schema generation, not actually used.
    # because DRF-YASG does not support partial.
    def get_fields(self):
        new_fields = OrderedDict()
        for name, field in super().get_fields().items():
            field.required = False
            new_fields[name] = field
        return new_fields


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


class CardMarkSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    mark = serializers.PrimaryKeyRelatedField(queryset=Mark.objects.all())

    def create(self, validated_data):
        card = Card.objects.get(pk=validated_data['card'])
        mark = validated_data['mark']
        card = CardMark(
            card=card,
            mark=mark
        )
        card.save()
        return card

class CardMarkDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    mark = serializers.PrimaryKeyRelatedField(queryset=Mark.objects.all())
    card = serializers.IntegerField()

    def create(self, validated_data):
        pass


class CardFileSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    file = serializers.FileField()

    def create(self, validated_data):
        card = Card.objects.get(pk=validated_data['card'])
        card_file = CardFile(
            card=card,
            file=validated_data['file']
        )
        card_file.save()
        return card_file


class CardFileDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    file = serializers.FileField()
    card = serializers.IntegerField()



class CardCommentSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    card = serializers.PrimaryKeyRelatedField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    body = serializers.CharField(max_length=300)
    created_on = serializers.DateTimeField(default=timezone.now)

    def create(self, validated_data):
        card = Card.objects.get(pk=validated_data['card'])
        card_comment = CardComment(
            card=card,
            user=validated_data['user'],
            body=validated_data['body'],
            created_on=validated_data['created_on']
        )
        card_comment.save()
        return card_comment

    def update(self, instance, validated_data):
        instance.body = validated_data.get('body', instance.body)
        instance.save()
        return instance


class CardCommentDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    card = serializers.PrimaryKeyRelatedField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)


class CardCommentUpdateSerializer(CardCommentSerializer):
    # Only for schema generation, not actually used.
    # because DRF-YASG does not support partial.
    def get_fields(self):
        new_fields = OrderedDict()
        for name, field in super().get_fields().items():
            field.required = False
            new_fields[name] = field
        return new_fields


class ProjectSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(max_length=50)
    owner = serializers.PrimaryKeyRelatedField(read_only=True)

    def create(self, validated_data):
        project = Project(
            title=validated_data['title'],
            owner=validated_data['owner']
        )
        project.save()
        return project

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.owner = validated_data.get('owner', instance.owner)
        instance.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['boards'] = BoardSerializer(instance.boards.all(), many=True, context=self.context).data
        return representation


class BoardsLastSeenSerializer(serializers.Serializer):
    timestamp = serializers.DateTimeField(read_only=True)


    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['board'] = BoardSerializer(instance.board, context=self.context).data
        return representation

