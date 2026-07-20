from django.db import connection
from django.utils import timezone
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        return Response({"status": "ok", "service": "family-chef-api"})


class DashboardView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        from apps.accounts.models import User
        from apps.dishes.models import Dish
        from apps.interactions.models import Comment, ContentReport
        from apps.recipes.models import RecipeArticle

        stats = {
            "users": User.objects.count(),
            "dishes": Dish.objects.count(),
            "publishedDishes": Dish.objects.filter(status=Dish.Status.PUBLISHED).count(),
            "pendingArticles": RecipeArticle.objects.filter(
                status=RecipeArticle.Status.PENDING_REVIEW
            ).count(),
            "pendingComments": Comment.objects.filter(status=Comment.Status.PENDING).count(),
            "pendingReports": ContentReport.objects.filter(
                status=ContentReport.Status.PENDING
            ).count(),
        }
        recent_dishes = list(
            Dish.objects.select_related("category")
            .values("id", "name", "status", "category__name", "updated_at")[:6]
        )
        return Response(
            {
                "stats": stats,
                "recentDishes": recent_dishes,
                "generatedAt": timezone.now(),
            }
        )
