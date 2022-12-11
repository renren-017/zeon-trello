from rest_framework import serializers

from api.serializers.card_serializers import CardSerializer
from boards.models import Board, Column


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
