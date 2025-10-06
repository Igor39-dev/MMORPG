from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
import random

from .models import Reply

@receiver(post_save, sender=Reply)
def notify_post_author_on_reply(sender, instance, created, **kwargs):
    """Оповещает автора поста, если на его объявление оставили отклик"""
    if created:
        subject = "Новый отклик на ваше объявление"
        message = (
            f"Здравствуйте, {instance.post.author.username}!\n\n"
            f"На ваше объявление «{instance.post.title}» оставлен отклик:\n\n"
            f"{instance.text}\n\n"
            f"Автор: {instance.author.username}"
        )
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [instance.post.author.email],
            fail_silently=True,
        )


@receiver(post_save, sender=Reply)
def notify_reply_author_on_accept(sender, instance, created, **kwargs):
    """Оповещает автора отклика, если его отклик приняли"""
    if not created and instance.is_accepted:
        subject = "Ваш отклик принят!"
        message = (
            f"Здравствуйте, {instance.author.username}!\n\n"
            f"Ваш отклик на объявление «{instance.post.title}» был принят."
        )
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [instance.author.email],
            fail_silently=True,
        )
