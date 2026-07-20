from collections import Counter, defaultdict
from random import Random

from django.db import transaction
from django.db.models import Prefetch

from apps.dishes.models import Dish
from apps.recipes.models import RecipeArticle, RecipeIngredient

from .models import MealPlan, MealPlanItem, MealPlanTemplate

DEFAULT_THEMES = [
    {
        "key": "balanced",
        "name": "营养均衡",
        "description": "兼顾荤素、主菜和快手家常菜。",
        "rules": {"prefer_categories": [], "avoid_tags": [], "max_minutes": 60},
        "sort_order": 10,
    },
    {
        "key": "fat_loss",
        "name": "减脂轻食",
        "description": "优先选择清淡、快手、蔬菜和高蛋白菜品。",
        "rules": {
            "prefer_keywords": ["鸡胸", "鱼", "虾", "蛋", "豆腐", "青菜", "西兰花"],
            "avoid_keywords": ["炸", "肥肠", "五花", "红烧肉", "糖"],
            "max_minutes": 45,
        },
        "sort_order": 20,
    },
    {
        "key": "homey",
        "name": "下饭家常",
        "description": "偏重家常热菜和味道更足的组合。",
        "rules": {"prefer_keywords": ["炒", "红烧", "炖", "肉", "蛋"], "max_minutes": 75},
        "sort_order": 30,
    },
    {
        "key": "quick_dinner",
        "name": "快手晚餐",
        "description": "适合下班后快速完成的一餐。",
        "rules": {"max_minutes": 30, "prefer_keywords": ["炒", "拌", "蛋"]},
        "sort_order": 40,
    },
    {
        "key": "solo",
        "name": "一人食",
        "description": "菜数少、耗时短，适合一个人轻松开饭。",
        "rules": {"target_count": 2, "max_minutes": 35, "prefer_keywords": ["饭", "面", "蛋"]},
        "sort_order": 50,
    },
    {
        "key": "guest",
        "name": "宴客硬菜",
        "description": "优先选择更有分量、适合招待朋友的菜。",
        "rules": {"prefer_keywords": ["肉", "鱼", "虾", "鸡", "排骨", "牛"], "max_minutes": 120},
        "sort_order": 60,
    },
]


def ensure_default_templates():
    for item in DEFAULT_THEMES:
        MealPlanTemplate.objects.update_or_create(
            key=item["key"],
            defaults={
                "name": item["name"],
                "description": item["description"],
                "rules": item["rules"],
                "sort_order": item["sort_order"],
                "status": MealPlanTemplate.Status.ACTIVE,
            },
        )


def published_dishes_queryset():
    ingredients = Prefetch(
        "article__current_version__ingredients",
        queryset=RecipeIngredient.objects.order_by("sort_order", "created_at"),
    )
    return (
        Dish.objects.filter(
            status=Dish.Status.PUBLISHED,
            article__status=RecipeArticle.Status.PUBLISHED,
            article__current_version__isnull=False,
        )
        .select_related("category", "article", "article__current_version")
        .prefetch_related("tags", ingredients)
    )


def as_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [item.strip() for item in str(value).split(",") if item.strip()]


def text_for_dish(dish):
    version = dish.article.current_version
    parts = [dish.name, dish.category.name]
    parts.extend(tag.name for tag in dish.tags.all())
    parts.extend(ingredient.raw_text for ingredient in version.ingredients.all())
    return " ".join(parts)


def snapshot_for_dish(dish):
    version = dish.article.current_version
    return {
        "name": dish.name,
        "categoryName": dish.category.name,
        "coverUrl": dish.cover_url,
        "recipeId": str(dish.article.id),
        "cookingMinutes": version.cooking_minutes,
        "difficulty": version.difficulty,
        "tags": [tag.name for tag in dish.tags.all()],
    }


def reason_for_dish(dish, theme, available_ingredients):
    matches = [item for item in available_ingredients if item and item in text_for_dish(dish)]
    if matches:
        return f"匹配已有食材：{'、'.join(matches[:3])}。"
    if theme:
        return f"符合“{theme.name}”主题，并补足本餐搭配。"
    return "从已发布菜谱中随机搭配，适合今天直接开做。"


def build_shopping_list(dishes):
    grouped = defaultdict(list)
    for dish in dishes:
        version = dish.article.current_version
        for ingredient in version.ingredients.all():
            key = ingredient.name or ingredient.raw_text.split(" ")[0]
            grouped[key].append(ingredient.raw_text)
    return [{"name": key, "items": values} for key, values in sorted(grouped.items())]


def score_dish(dish, *, theme_rules, avoid_keywords, available_ingredients, max_minutes):
    version = dish.article.current_version
    dish_text = text_for_dish(dish)
    if max_minutes and version.cooking_minutes > max_minutes:
        return None
    if any(keyword in dish_text for keyword in avoid_keywords):
        return None

    score = 10
    prefer_keywords = as_list(theme_rules.get("prefer_keywords")) + available_ingredients
    avoid_theme_keywords = as_list(theme_rules.get("avoid_keywords"))
    score += sum(5 for keyword in prefer_keywords if keyword and keyword in dish_text)
    score -= sum(8 for keyword in avoid_theme_keywords if keyword and keyword in dish_text)
    score += min(dish.like_count, 20)
    score += min(dish.comment_count, 10)
    if version.difficulty in {"easy", "basic"}:
        score += 2
    return max(score, 1)


def select_dishes(candidates, target_count, seed):
    rng = Random(seed)
    picked = []
    category_counts = Counter()
    tag_counts = Counter()
    pool = list(candidates)

    while pool and len(picked) < target_count:
        weighted = []
        for dish, base_score in pool:
            category_penalty = category_counts[dish.category_id] * 4
            dish_tag_names = [tag.name for tag in dish.tags.all()]
            tag_penalty = sum(tag_counts[name] for name in dish_tag_names)
            score = max(base_score - category_penalty - tag_penalty, 1)
            weighted.append((dish, score))

        total = sum(score for _, score in weighted)
        cursor = rng.uniform(0, total)
        upto = 0
        chosen = weighted[-1][0]
        for dish, score in weighted:
            upto += score
            if upto >= cursor:
                chosen = dish
                break

        picked.append(chosen)
        category_counts[chosen.category_id] += 1
        for tag in chosen.tags.all():
            tag_counts[tag.name] += 1
        pool = [(dish, score) for dish, score in pool if dish.id != chosen.id]

    return picked


@transaction.atomic
def generate_meal_plan(data, user=None, persist=False):
    mode = data.get("mode") or MealPlan.Mode.RANDOM
    theme_key = data.get("themeKey") or data.get("theme_key") or ""
    theme = None
    if mode == MealPlan.Mode.THEME and theme_key:
        theme = MealPlanTemplate.objects.filter(
            key=theme_key, status=MealPlanTemplate.Status.ACTIVE
        ).first()

    theme_rules = theme.rules if theme else {}
    servings = int(data.get("servings") or 2)
    target_count = int(
        data.get("targetCount") or data.get("target_count") or theme_rules.get("target_count") or 4
    )
    target_count = max(1, min(target_count, 8))
    meal_type = data.get("mealType") or data.get("meal_type") or MealPlan.MealType.DINNER
    max_minutes = (
        data.get("maxMinutes")
        or data.get("max_minutes")
        or theme_rules.get("max_minutes")
    )
    max_minutes = int(max_minutes) if max_minutes else None
    avoid_keywords = as_list(data.get("avoidKeywords") or data.get("avoid_keywords"))
    available_ingredients = as_list(
        data.get("availableIngredients") or data.get("available_ingredients")
    )
    category_keys = as_list(data.get("categoryKeys") or data.get("category_keys"))
    exclude_dish_ids = {str(item) for item in as_list(data.get("excludeDishIds"))}

    queryset = published_dishes_queryset()
    if category_keys:
        queryset = queryset.filter(category__key__in=category_keys)
    if exclude_dish_ids:
        queryset = queryset.exclude(id__in=exclude_dish_ids)

    candidates = []
    for dish in queryset.distinct():
        score = score_dish(
            dish,
            theme_rules=theme_rules,
            avoid_keywords=avoid_keywords,
            available_ingredients=available_ingredients,
            max_minutes=max_minutes,
        )
        if score is not None:
            candidates.append((dish, score))

    if not candidates and max_minutes:
        for dish in published_dishes_queryset().distinct():
            score = score_dish(
                dish,
                theme_rules=theme_rules,
                avoid_keywords=avoid_keywords,
                available_ingredients=available_ingredients,
                max_minutes=None,
            )
            if score is not None:
                candidates.append((dish, score))

    if not candidates:
        raise ValueError("暂时没有符合条件的菜品，请放宽筛选条件。")

    seed = data.get("seed") or f"{mode}:{theme_key}:{servings}:{target_count}:{len(candidates)}"
    dishes = select_dishes(candidates, target_count, seed)
    total_minutes = sum(dish.article.current_version.cooking_minutes for dish in dishes)
    theme_name = theme.name if theme else "随机"
    meal_type_label = (
        MealPlan.MealType(meal_type).label if meal_type in MealPlan.MealType.values else "一餐"
    )
    title = data.get("title") or f"{theme_name}{meal_type_label} {len(dishes)} 菜方案"
    preferences = {
        "categoryKeys": category_keys,
        "avoidKeywords": avoid_keywords,
        "availableIngredients": available_ingredients,
        "maxMinutes": max_minutes,
    }
    summary = (
        f"为 {servings} 人搭配 {len(dishes)} 道菜，"
        f"预计总烹饪时间约 {total_minutes} 分钟。"
    )

    plan = MealPlan.objects.create(
        user=user if persist and user and user.is_authenticated else None,
        title=title,
        mode=mode,
        theme_key=theme_key,
        servings=servings,
        meal_type=meal_type,
        target_count=target_count,
        preferences=preferences,
        summary=summary,
        total_minutes=total_minutes,
        shopping_list=build_shopping_list(dishes),
        status=(
            MealPlan.Status.SAVED
            if persist and user and user.is_authenticated
            else MealPlan.Status.DRAFT
        ),
    )

    for index, dish in enumerate(dishes):
        MealPlanItem.objects.create(
            plan=plan,
            dish=dish,
            recipe=dish.article,
            sort_order=index,
            reason=reason_for_dish(dish, theme, available_ingredients),
            snapshot=snapshot_for_dish(dish),
        )

    return plan
