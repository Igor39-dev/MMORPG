# Create your models here.
from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
from django.conf import settings
from django.utils import timezone
import secrets
import string
from django.contrib.auth.models import AbstractUser

class OneTimeCode(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='one_time_codes'
    )
    code = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    ttl_seconds = models.PositiveIntegerField(default=120)

    def is_expired(self):
        return (timezone.now() - self.created_at).total_seconds() > self.ttl_seconds

    def __str__(self):
        return f'{self.user.username}: {self.code}'

    @classmethod
    def generate_for_user(cls, user, ttl_seconds=60):
        alphabet = string.digits
        code = ''.join(secrets.choice(alphabet) for _ in range(5))
        return cls.objects.create(user=user, code=code, ttl_seconds=ttl_seconds)


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
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    is_verified = models.BooleanField(default=False)

