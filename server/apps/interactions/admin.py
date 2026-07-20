from django.contrib import admin

from .models import Comment, CommentReaction, ContentReport, DishReaction

admin.site.register(Comment)
admin.site.register(DishReaction)
admin.site.register(CommentReaction)
admin.site.register(ContentReport)
