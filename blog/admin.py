from django.contrib import admin
from .models import Article, Comment, Like

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at')
    list_filter = ('created_at', 'author')
    search_fields = ('title', 'content')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('article', 'author', 'created_at')

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('article', 'user', 'created_at')