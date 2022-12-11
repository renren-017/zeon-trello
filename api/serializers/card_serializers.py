from collections import OrderedDict

from django.utils import timezone
from rest_framework import serializers

from boards.models import Column, Card, Mark, CardMark, CardFile, CardComment


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
