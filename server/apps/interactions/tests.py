import pytest
from django.urls import reverse

from apps.accounts.models import User
from apps.dishes.models import Dish, DishCategory

from .models import Comment, ContentReport, DishReaction


@pytest.fixture
def published_dish(db):
    category = DishCategory.objects.create(key="test-dish", name="测试菜品")
    return Dish.objects.create(
        legacy_id="test-interaction-dish",
        name="互动测试菜",
        slug="test-interaction-dish",
        category=category,
        status=Dish.Status.PUBLISHED,
    )


@pytest.fixture
def member(db):
    return User.objects.create_user(username="interaction-user", password="strong-pass-123")


@pytest.mark.django_db
def test_dish_reaction_state_and_switch(api_client, member, published_dish):
    api_client.force_authenticate(member)
    url = reverse("dish-reaction", args=[published_dish.id])

    initial = api_client.get(url)
    liked = api_client.post(url, {"value": 1}, format="json")
    disliked = api_client.post(url, {"value": -1}, format="json")
    cleared = api_client.post(url, {"value": 0}, format="json")

    assert initial.data == {"value": 0, "likeCount": 0, "dislikeCount": 0}
    assert liked.data == {"value": 1, "likeCount": 1, "dislikeCount": 0}
    assert disliked.data == {"value": -1, "likeCount": 0, "dislikeCount": 1}
    assert cleared.data == {"value": 0, "likeCount": 0, "dislikeCount": 0}
    assert not DishReaction.objects.filter(dish=published_dish, user=member).exists()


@pytest.mark.django_db
def test_pending_comment_is_not_public(api_client, member, published_dish):
    api_client.force_authenticate(member)
    created = api_client.post(
        reverse("comments-list"),
        {"dish": str(published_dish.id), "content": "等待审核的评论"},
        format="json",
    )

    api_client.force_authenticate(user=None)
    public_comments = api_client.get(reverse("comments-list"), {"dish": published_dish.id})

    assert created.status_code == 201
    assert created.data["status"] == Comment.Status.PENDING
    assert public_comments.data["count"] == 0


@pytest.mark.django_db
def test_comment_reaction_and_delete_permissions(api_client, member, published_dish):
    comment = Comment.objects.create(
        dish=published_dish,
        user=member,
        content="公开评论",
        status=Comment.Status.VISIBLE,
    )
    other_user = User.objects.create_user(username="other-user", password="strong-pass-123")
    api_client.force_authenticate(other_user)

    reacted = api_client.post(
        reverse("comments-reaction", args=[comment.id]),
        {"value": 1},
        format="json",
    )
    forbidden = api_client.delete(reverse("comments-detail", args=[comment.id]))

    assert reacted.status_code == 200
    assert reacted.data["my_reaction"] == 1
    assert reacted.data["like_count"] == 1
    assert forbidden.status_code == 403


@pytest.mark.django_db
def test_member_can_report_dish(api_client, member, published_dish):
    api_client.force_authenticate(member)
    response = api_client.post(
        reverse("reports-list"),
        {
            "target_type": ContentReport.TargetType.DISH,
            "target_id": str(published_dish.id),
            "reason": "内容错误",
            "description": "材料信息需要核对",
        },
        format="json",
    )

    assert response.status_code == 201
    assert ContentReport.objects.filter(reporter=member, target_id=published_dish.id).exists()


@pytest.mark.django_db
def test_report_rejects_unknown_target(api_client, member):
    api_client.force_authenticate(member)
    response = api_client.post(
        reverse("reports-list"),
        {
            "target_type": ContentReport.TargetType.DISH,
            "target_id": "00000000-0000-0000-0000-000000000000",
            "reason": "内容错误",
        },
        format="json",
    )

    assert response.status_code == 400
