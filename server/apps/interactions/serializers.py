from rest_framework import serializers

from .models import Comment, ContentReport


class CommentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Comment
        fields = [
            "id",
            "dish",
            "user",
            "username",
            "parent",
            "root",
            "content",
            "status",
            "like_count",
            "dislike_count",
            "moderation_note",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "root",
            "status",
            "like_count",
            "dislike_count",
            "moderation_note",
            "created_at",
        ]


class ModerationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["status", "moderation_note"]


class ReactionSerializer(serializers.Serializer):
    value = serializers.ChoiceField(choices=[-1, 0, 1])


class ReportSerializer(serializers.ModelSerializer):
    reporter_name = serializers.CharField(source="reporter.username", read_only=True)

    class Meta:
        model = ContentReport
        fields = "__all__"
        read_only_fields = ["id", "reporter", "handled_by", "status", "resolution"]
