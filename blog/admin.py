from django.contrib import admin
from .models import Post, Comment

admin.site.register(Post)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("post", "body", "created_on", "approve")
    list_filter = ("created_on", "approve")
    search_fields = ("body", "post")
    actions = [
        "approve_comments",
    ]

    def approve_comments(self, request, queryset):
        queryset.update(approve=True)
