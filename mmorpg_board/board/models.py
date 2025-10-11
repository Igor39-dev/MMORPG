from datetime import timedelta
from django.db import models
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField 
from django.conf import settings
from django.utils import timezone
import secrets
import string
from django.contrib.auth.models import AbstractUser


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = RichTextUploadingField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='posts')

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
        ]


class Reply(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_replies')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_replies')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_accepted = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Отклик от {self.user.username} на {self.post.title[:20]}'


class CustomUser(AbstractUser):
    is_verified = models.BooleanField(default=False)
    confirmation_token = models.CharField(max_length=6, blank=True, null=True)
    token_created_at = models.DateTimeField(auto_now_add=True)

    def generate_confirmation_token(self):
        alphabet = string.digits
        self.confirmation_token = ''.join(secrets.choice(alphabet) for _ in range(6))
        self.token_created_at = timezone.now()
        self.save()

    def is_token_valid(self):
        return self.token_created_at >= timezone.now() - timedelta(minutes=2)

    def clear_confirmation_token(self):
        self.confirmation_token = None
        self.save()
        