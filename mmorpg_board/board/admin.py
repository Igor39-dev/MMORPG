from django.contrib import admin
from .models import Post, Reply, OneTimeCode

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'created_at', 'is_active')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('title', 'content', 'author__username')

@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'is_accepted', 'is_deleted', 'created_at')
    list_filter = ('is_accepted', 'is_deleted', 'created_at')
    search_fields = ('text', 'author__username', 'post__title')

@admin.register(OneTimeCode)
class OneTimeCodeAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'created_at', 'ttl_seconds')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'code')
