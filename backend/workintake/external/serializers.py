from rest_framework import serializers

from .models import WorkItem


class CreateWorkItemSerializer(serializers.ModelSerializer):
    external_id = serializers.CharField(max_length=255, required=True)
    title = serializers.CharField(max_length=255, required=True)
    description = serializers.CharField(max_length=1000, required=True)

    class Meta:
        model = WorkItem
        fields = [
            "external_id",
            "title",
            "description",
        ]


class ListWorkItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkItem
        fields = [
            "uid",
            "external_id",
            "title",
            "description",
            "status",
            "analysisResult",
            "analysisError",
            "retryCount",
        ]
