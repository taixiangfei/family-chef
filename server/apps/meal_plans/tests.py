import pytest
from django.urls import reverse

from apps.accounts.models import User
from apps.dishes.models import Dish, DishCategory
from apps.recipes.models import RecipeArticle, RecipeIngredient, RecipeVersion

from .models import MealPlan, MealPlanTemplate


@pytest.fixture
def member(db):
    return User.objects.create_user(username="meal-user", password="strong-pass-123")


@pytest.fixture
def recipe_dishes(db):
    category = DishCategory.objects.create(key="meal-test", name="测试分类")
    dishes = []
    for index in range(5):
        dish = Dish.objects.create(
            legacy_id=f"meal-dish-{index}",
            name=f"测试配菜 {index}",
            slug=f"meal-dish-{index}",
            category=category,
            status=Dish.Status.PUBLISHED,
        )
        article = RecipeArticle.objects.create(
            dish=dish,
            title=dish.name,
            status=RecipeArticle.Status.PUBLISHED,
        )
        version = RecipeVersion.objects.create(
            article=article,
            version_no=1,
            summary="测试摘要",
            cooking_minutes=20 + index,
            difficulty=RecipeVersion.Difficulty.BASIC,
            servings=2,
        )
        RecipeIngredient.objects.create(
            version=version,
            raw_text=f"鸡蛋 {index + 1} 个",
            name="鸡蛋",
            sort_order=0,
        )
        article.current_version = version
        article.save(update_fields=["current_version", "updated_at"])
        dishes.append(dish)
    return dishes


@pytest.mark.django_db
def test_anonymous_can_generate_meal_plan(api_client, recipe_dishes):
    response = api_client.post(
        reverse("meal-plans-generate"),
        {"mode": "random", "servings": 2, "targetCount": 3},
        format="json",
    )

    assert response.status_code == 201
    assert response.data["status"] == MealPlan.Status.DRAFT
    assert len(response.data["items"]) == 3


@pytest.mark.django_db
def test_member_can_save_generated_meal_plan(api_client, member, recipe_dishes):
    generated = api_client.post(
        reverse("meal-plans-generate"),
        {"mode": "random", "targetCount": 2},
        format="json",
    )
    api_client.force_authenticate(member)
    saved = api_client.post(reverse("meal-plans-save", args=[generated.data["id"]]))

    assert saved.status_code == 200
    assert saved.data["isSaved"] is True
    assert MealPlan.objects.get(pk=generated.data["id"]).user == member


@pytest.mark.django_db
def test_user_only_sees_own_saved_meal_plans(api_client, member, recipe_dishes):
    other = User.objects.create_user(username="other-meal-user", password="strong-pass-123")
    MealPlan.objects.create(user=other, title="别人的方案", mode=MealPlan.Mode.RANDOM)
    own = MealPlan.objects.create(
        user=member,
        title="自己的方案",
        mode=MealPlan.Mode.RANDOM,
        status=MealPlan.Status.SAVED,
    )

    api_client.force_authenticate(member)
    response = api_client.get(reverse("meal-plans-list"))

    assert response.status_code == 200
    assert [item["id"] for item in response.data["results"]] == [str(own.id)]


@pytest.mark.django_db
def test_themes_endpoint_seeds_default_templates(api_client):
    response = api_client.get(reverse("meal-plan-themes-list"))

    assert response.status_code == 200
    assert MealPlanTemplate.objects.filter(key="balanced").exists()
    assert any(item["key"] == "fat_loss" for item in response.data)
