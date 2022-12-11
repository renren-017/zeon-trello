from rest_framework import serializers

from api.serializers.board_serializers import BoardSerializer
from boards.models import Project


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
