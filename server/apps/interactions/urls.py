from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AdminCommentViewSet, CommentViewSet, DishReactionViewSet, ReportViewSet

router = DefaultRouter()
router.register("comments", CommentViewSet, basename="comments")
router.register("reports", ReportViewSet, basename="reports")
router.register("admin/comments", AdminCommentViewSet, basename="admin-comments")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "dishes/<uuid:dish_id>/reaction/",
        DishReactionViewSet.as_view({"get": "retrieve", "post": "create"}),
        name="dish-reaction",
    ),
]
