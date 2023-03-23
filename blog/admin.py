from django.contrib import admin
from .models import Post, Comment, Category, ProfileSettings, Notification


admin.site.register(Category)
admin.site.register(Post)
admin.site.register(ProfileSettings)
admin.site.register(Notification)
admin.site.register(Comment)
