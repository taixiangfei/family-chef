from rest_framework import serializers

from apps.dishes.models import Dish

from .models import Comment, ContentReport


class CommentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    user_display_name = serializers.SerializerMethodField()
    my_reaction = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            "id",
            "dish",
            "user",
            "username",
            "user_display_name",
            "parent",
            "root",
            "content",
            "status",
            "like_count",
            "dislike_count",
            "my_reaction",
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

    def get_user_display_name(self, obj):
        return obj.user.nickname or obj.user.username

    def validate(self, attrs):
        dish = attrs.get("dish")
        parent = attrs.get("parent")
        if dish and dish.status != Dish.Status.PUBLISHED:
            raise serializers.ValidationError({"dish": "只能评论已发布的菜品。"})
        if parent and dish and parent.dish_id != dish.id:
            raise serializers.ValidationError({"parent": "回复必须属于同一道菜。"})
        return attrs

    def get_my_reaction(self, obj):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return 0
        reaction = obj.reactions.filter(user=request.user).values_list("value", flat=True).first()
        return reaction or 0


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

    def validate(self, attrs):
        target_type = attrs.get("target_type")
        target_id = attrs.get("target_id")
        if target_type == ContentReport.TargetType.DISH:
            exists = Dish.objects.filter(pk=target_id, status=Dish.Status.PUBLISHED).exists()
        else:
            exists = Comment.objects.filter(pk=target_id, status=Comment.Status.VISIBLE).exists()
        if not exists:
            raise serializers.ValidationError({"target_id": "举报目标不存在或不可见。"})
        return attrs
