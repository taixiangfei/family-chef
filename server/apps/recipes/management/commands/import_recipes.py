import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from apps.dishes.models import Dish, DishCategory, Tag
from apps.recipes.models import (
    RecipeArticle,
    RecipeIngredient,
    RecipeStep,
    RecipeVersion,
)

DIFFICULTY_MAP = {
    "入门": RecipeVersion.Difficulty.EASY,
    "简单": RecipeVersion.Difficulty.EASY,
    "基础": RecipeVersion.Difficulty.BASIC,
    "中等": RecipeVersion.Difficulty.MEDIUM,
    "进阶": RecipeVersion.Difficulty.MEDIUM,
    "困难": RecipeVersion.Difficulty.HARD,
}


class Command(BaseCommand):
    help = "Import normalized cookbook JSON into dishes and recipe articles."

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            default="data/recipes.json",
            help="Path to the normalized cookbook JSON file.",
        )
        parser.add_argument(
            "--publish",
            action="store_true",
            help="Publish imported dishes and recipe articles immediately.",
        )

    def handle(self, *args, **options):
        source = Path(options["file"])
        if not source.is_absolute():
            source = Path.cwd() / source
        if not source.exists():
            raise CommandError(f"Recipe file does not exist: {source}")

        try:
            payload = json.loads(source.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise CommandError(f"Invalid recipe JSON: {exc}") from exc

        recipes = payload.get("recipes")
        if not isinstance(recipes, list):
            raise CommandError("Recipe JSON must contain a recipes array.")

        with transaction.atomic():
            categories = self.import_categories(payload.get("categories", []))
            tags = self.import_tags(payload.get("tags", []))
            counts = self.import_recipes(recipes, categories, tags, options["publish"])

        self.stdout.write(
            self.style.SUCCESS(
                "Imported "
                f"{counts['recipes']} recipes, {counts['categories']} categories, "
                f"{counts['tags']} tags, {counts['ingredients']} ingredients and "
                f"{counts['steps']} steps."
            )
        )

    def import_categories(self, values):
        categories = {}
        for index, item in enumerate(values):
            key = item.get("key")
            name = item.get("label") or item.get("name")
            if not key or not name or key == "all":
                continue
            category, _ = DishCategory.objects.update_or_create(
                key=key,
                defaults={
                    "name": name,
                    "sort_order": index,
                    "status": DishCategory.Status.ACTIVE,
                },
            )
            categories[key] = category
        return categories

    def import_tags(self, values):
        tags = {}
        for value in values:
            name = value.get("name") if isinstance(value, dict) else value
            if not name:
                continue
            tag, _ = Tag.objects.update_or_create(
                name=name,
                defaults={"type": Tag.Type.METHOD, "status": Tag.Status.ACTIVE},
            )
            tags[name] = tag
        return tags

    def import_recipes(self, values, categories, tags, publish):
        counts = {
            "recipes": 0,
            "categories": len(categories),
            "tags": len(tags),
            "ingredients": 0,
            "steps": 0,
        }
        for item in values:
            category = categories.get(item.get("category"))
            if category is None:
                self.stderr.write(f"Skipped recipe without category: {item.get('id')}")
                continue

            legacy_id = str(item.get("id") or "").strip()
            name = str(item.get("title") or "").strip()
            if not legacy_id or not name:
                self.stderr.write("Skipped recipe without id or title.")
                continue

            published = publish
            dish, _ = Dish.objects.update_or_create(
                legacy_id=legacy_id,
                defaults={
                    "name": name,
                    "slug": legacy_id[:180],
                    "category": category,
                    "cover_url": item.get("image") or "",
                    "status": Dish.Status.PUBLISHED if published else Dish.Status.DRAFT,
                    "source_project": item.get("source") or "",
                    "source_path": item.get("sourcePath") or "",
                    "source_url": item.get("sourceUrl") or "",
                },
            )
            dish.tags.set(
                [tags[tag_name] for tag_name in self.recipe_tag_names(item) if tag_name in tags]
            )

            article, _ = RecipeArticle.objects.get_or_create(
                dish=dish,
                defaults={"title": name},
            )
            article.title = name
            article.status = (
                RecipeArticle.Status.PUBLISHED if published else RecipeArticle.Status.DRAFT
            )
            article.published_at = timezone.now() if published else None
            article.save(update_fields=["title", "status", "published_at", "updated_at"])

            version = self.import_version(article, item)
            if published and article.current_version_id != version.id:
                article.current_version = version
                article.save(update_fields=["current_version", "updated_at"])

            counts["recipes"] += 1
            counts["ingredients"] += len(item.get("ingredients") or [])
            counts["steps"] += len(item.get("steps") or [])
        return counts

    def recipe_tag_names(self, item):
        names = list(item.get("tags") or [])
        method = item.get("method")
        if method and method not in names:
            names.append(method)
        return dict.fromkeys(names)

    def import_version(self, article, item):
        version, _ = RecipeVersion.objects.get_or_create(article=article, version_no=1)
        version.summary = item.get("summary") or ""
        version.cooking_minutes = max(0, int(item.get("time") or 20))
        version.difficulty = DIFFICULTY_MAP.get(
            item.get("difficulty"), RecipeVersion.Difficulty.BASIC
        )
        version.servings = max(1, int(item.get("servings") or 1))
        version.tips = item.get("tips") or []
        version.change_note = "从 front/src/utils/cookbook.js 导入"
        version.save()

        version.ingredients.all().delete()
        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(
                    version=version,
                    name=str(raw),
                    raw_text=str(raw),
                    sort_order=index,
                )
                for index, raw in enumerate(item.get("ingredients") or [])
                if str(raw).strip()
            ]
        )

        version.steps.all().delete()
        RecipeStep.objects.bulk_create(
            [
                RecipeStep(version=version, description=str(raw), sort_order=index)
                for index, raw in enumerate(item.get("steps") or [])
                if str(raw).strip()
            ]
        )
        return version
