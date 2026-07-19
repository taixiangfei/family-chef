import pytest
from django.urls import reverse

from apps.accounts.models import User
from apps.dishes.models import Dish, DishCategory

from .models import RecipeArticle


@pytest.mark.django_db
def test_admin_can_create_version_and_publish_article(api_client):
    admin = User.objects.create_superuser(
        username="content-admin",
        password="strong-pass-123",
    )
    category = DishCategory.objects.create(key="content-test", name="内容测试")
    dish = Dish.objects.create(
        legacy_id="content-test-dish",
        name="内容测试菜",
        slug="content-test-dish",
        category=category,
        status=Dish.Status.DRAFT,
    )
    api_client.force_authenticate(admin)

    created = api_client.post(
        reverse("admin-articles-list"),
        {"dish": str(dish.id), "title": "内容测试菜", "status": "draft"},
        format="json",
    )
    article_id = created.data["id"]
    version = api_client.post(
        reverse("admin-articles-versions", args=[article_id]),
        {
            "summary": "后台编辑的教程摘要",
            "cooking_minutes": 25,
            "difficulty": "basic",
            "servings": 2,
            "tips": ["先准备好全部材料"],
            "change_note": "首版",
            "ingredients": [
                {"name": "鸡蛋", "raw_text": "鸡蛋 2 个", "sort_order": 0}
            ],
            "steps": [{"description": "鸡蛋打散。", "sort_order": 0}],
        },
        format="json",
    )
    detail = api_client.get(reverse("admin-articles-detail", args=[article_id]))
    published = api_client.post(
        reverse("admin-articles-publish", args=[article_id]),
        {"versionId": version.data["id"]},
        format="json",
    )

    assert created.status_code == 201
    assert version.status_code == 201
    assert detail.data["latest_version"]["summary"] == "后台编辑的教程摘要"
    assert detail.data["version_count"] == 1
    assert published.status_code == 200
    assert published.data["status"] == RecipeArticle.Status.PUBLISHED
    dish.refresh_from_db()
    assert dish.status == Dish.Status.PUBLISHED
