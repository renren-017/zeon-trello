from collections import OrderedDict

from rest_framework import serializers
from boards.models import Project, Board, Column, Card, Mark, CardComment, CardFile, BoardMember, BoardFavourite, \
    BoardLastSeen
from django.contrib.auth import get_user_model
from django.utils import timezone


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
        project = Project.objects.get(pk=validated_data['project'])
        board = Board(title=validated_data['title'],
                      project=project,
                      background_img=validated_data['background_img'])
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
        new_fields = OrderedDict()
        for name, field in super().get_fields().items():
            field.required = False
            new_fields[name] = field
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
        representation['bars'] = BarSerializer(instance.bars.all(), many=True, context=self.context).data
        representation['members'] = UserSerializer(members, many=True, context=self.context).data
        return representation


class BoardFavouriteSerializer(serializers.Serializer):
    board = serializers.IntegerField(read_only=True)
    user = serializers.IntegerField(read_only=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


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
    board = serializers.PrimaryKeyRelatedField(read_only=True)
    title = serializers.CharField(max_length=30)

    def create(self, validated_data):
        board = Board.objects.get(pk=validated_data['board'])
        bar = Column(
            board=board,
            title=validated_data['title']
        )
        bar.save()

        return bar

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['cards'] = CardSerializer(instance.cards.all(), many=True, context=self.context).data
        return representation


class CardSerializer(serializers.Serializer):
    bar = serializers.CharField()
    title = serializers.CharField(max_length=30)
    description = serializers.CharField(max_length=500)
    deadline = serializers.DateTimeField()

    def create(self, validated_data):
        bar = Column.objects.get(pk=validated_data['bar'])
        card = Card(
            bar=bar,
            title=validated_data['title'],
            description=validated_data['description'],
            deadline=validated_data['deadline'],
        )

        card.save()
        return card

    def update(self, instance, validated_data):
        pass


class CardLabelSerializer(serializers.Serializer):
    card = serializers.CharField()
    title = serializers.CharField(max_length=30)
    color = serializers.CharField(default='#000', max_length=7)

    def create(self, validated_data):
        card = Card.objects.get(pk=validated_data['card'])
        card = Mark(
            card=card,
            title=validated_data['title'],
            color=validated_data['color']
        )
        card.save()
        return card


class CardFileSerializer(serializers.Serializer):
    card = serializers.CharField()
    file = serializers.FileField()

    def create(self, validated_data):
        card = Card.objects.get(pk=validated_data['card'])
        card_file = CardFile(
            card=card,
            file=validated_data['file']
        )
        card_file.save()
        return card_file


class CardCommentSerializer(serializers.Serializer):
    card = serializers.CharField()
    user = serializers.StringRelatedField(read_only=True)
    body = serializers.CharField(max_length=300)
    created_on = serializers.DateTimeField(default=timezone.now)

    def create(self, validated_data):
        card = Card.objects.get(pk=validated_data['card'])
        card_comment = CardComment(
            card=card,
            body=validated_data['body'],
            created_on=validated_data['created_on']
        )
        card_comment.save()
        return card_comment.save()


class CardChecklistItemSerializer(serializers.Serializer):
    card = serializers.CharField()
    content = serializers.CharField(max_length=300)
    is_done = serializers.BooleanField(default=False)

    def create(self, validated_data):
        card = Card.objects.get(pk=validated_data['card'])
        card_checklist_item = CardComment(
            card=card,
            body=validated_data['content'],
            is_done=validated_data['is_done'],
        )
        card_checklist_item.save()
        return card_checklist_item.save()


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

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['board'] = BoardSerializer(instance.board, context=self.context).data
        return representation

