from datetime import timedelta
from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
from django.conf import settings
from django.utils import timezone
import secrets
import string
from django.contrib.auth.models import AbstractUser


class Post(models.Model):
    CATEGORY_CHOICES = [
        ('TANK', 'Танки'),
        ('HEAL', 'Хилы'),
        ('DD', 'ДД'),
        ('TRADER', 'Торговцы'),
        ('GUILDMASTER', 'Гилдмастеры'),
        ('QUESTGIVER', 'Квестгиверы'),
        ('BLACKSMITH', 'Кузнецы'),
        ('LEATHERWORKER', 'Кожевники'),
        ('ALCHEMIST', 'Зельевары'),
        ('SPELLMASTER', 'Мастера заклинаний'),
    ]

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='posts'
    )
    title = models.CharField(max_length=255)
    content = CKEditor5Field('Text', config_name='default')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Reply(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='replies')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='replies'
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_accepted = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Отклик от {self.author.username} на {self.post.title[:20]}'


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
