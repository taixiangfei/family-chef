import pytest
from django.urls import reverse

from apps.dishes.models import Dish, DishCategory, Tag
from apps.recipes.models import RecipeArticle, RecipeVersion


@pytest.mark.django_db
def test_public_dishes_filter_by_category_key_and_expose_recipe_preview(api_client):
    category = DishCategory.objects.create(key="vegetable", name="素菜")
    tag = Tag.objects.create(name="炒", type=Tag.Type.METHOD)
    dish = Dish.objects.create(
        legacy_id="hoc-test-tomato-egg",
        name="番茄炒蛋",
        slug="hoc-test-tomato-egg",
        category=category,
        status=Dish.Status.PUBLISHED,
    )
    dish.tags.add(tag)
    article = RecipeArticle.objects.create(
        dish=dish,
        title="番茄炒蛋",
        status=RecipeArticle.Status.PUBLISHED,
    )
    version = RecipeVersion.objects.create(
        article=article,
        version_no=1,
        summary="酸甜开胃",
        cooking_minutes=15,
        servings=2,
    )
    article.current_version = version
    article.save(update_fields=["current_version"])

    response = api_client.get(
        reverse("dishes-list"),
        {"category": "vegetable", "search": "番茄"},
    )

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["recipe_id"] == str(article.id)
    assert response.data["results"][0]["recipe_summary"] == "酸甜开胃"


@pytest.mark.django_db
def test_public_recipe_detail_supports_legacy_id(api_client):
    category = DishCategory.objects.create(key="staple", name="主食")
    dish = Dish.objects.create(
        legacy_id="hoc-test-noodles",
        name="家常面",
        slug="hoc-test-noodles",
        category=category,
        status=Dish.Status.PUBLISHED,
    )
    article = RecipeArticle.objects.create(
        dish=dish,
        title="家常面",
        status=RecipeArticle.Status.PUBLISHED,
    )
    version = RecipeVersion.objects.create(
        article=article,
        version_no=1,
        summary="简单快手",
    )
    article.current_version = version
    article.save(update_fields=["current_version"])

    response = api_client.get(reverse("recipes-by-legacy", args=[dish.legacy_id]))

    assert response.status_code == 200
    assert response.data["dish"]["legacy_id"] == dish.legacy_id
    assert response.data["current_version"]["summary"] == "简单快手"


@pytest.mark.django_db
def test_public_dishes_hide_unpublished_content(api_client):
    category = DishCategory.objects.create(key="soup", name="汤羹")
    dish = Dish.objects.create(
        legacy_id="hoc-test-hidden-soup",
        name="下架汤品",
        slug="hoc-test-hidden-soup",
        category=category,
        status=Dish.Status.UNPUBLISHED,
    )
    RecipeArticle.objects.create(
        dish=dish,
        title="下架汤品",
        status=RecipeArticle.Status.UNPUBLISHED,
    )

    response = api_client.get(reverse("dishes-list"))

    assert response.status_code == 200
    assert response.data["count"] == 0


@pytest.mark.django_db
def test_public_dishes_allow_h5_cors_origin(api_client):
    response = api_client.get(
        reverse("dishes-list"),
        HTTP_ORIGIN="http://127.0.0.1:5173",
    )

    assert response.status_code == 200
    assert response["access-control-allow-origin"] == "http://127.0.0.1:5173"
