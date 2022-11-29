from rest_framework import serializers
from boards.models import Board, Bar, Card, CardLabel, CardComment, CardFile, CardChecklistItem

from django.utils import timezone


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
        board.save()

        return board

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.background_img = validated_data.get('background_img', instance.background_img)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.is_starred = validated_data.get('is_starred', instance.is_starred)
        instance.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['bars'] = BarSerializer(instance.bars.all(), many=True, context=self.context).data
        return representation




class BarSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    board = serializers.CharField()
    title = serializers.CharField(max_length=30)

    def create(self, validated_data):
        board = Board.objects.get(pk=validated_data['board'])
        bar = Bar(
            board=board,
            title=validated_data['title']
        )
        bar.save()

        return bar

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
        bar = Bar.objects.get(pk=validated_data['bar'])
        card = Card(
            bar=bar,
            title=validated_data['title'],
            description=validated_data['description'],
            deadline=validated_data['deadline'],
        )

        card.save()
        return card


class CardLabelSerializer(serializers.Serializer):
    card = serializers.CharField()
    title = serializers.CharField(max_length=30)
    color = serializers.CharField(default='#000', max_length=7)

    def create(self, validated_data):
        card = Card.objects.get(pk=validated_data['card'])
        card = CardLabel(
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