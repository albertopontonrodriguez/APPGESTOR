from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class ChatRoom(TimeStampedModel):
    name = models.CharField(max_length=140)
    description = models.TextField(blank=True)
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='chat_rooms')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='created_chat_rooms', null=True, blank=True)
    is_direct = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Sala de chat'
        verbose_name_plural = 'Salas de chat'
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def last_message(self):
        return self.messages.order_by('-created_at').first()


class ChatMessage(TimeStampedModel):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_messages')
    body = models.TextField()
    attachment = models.FileField(upload_to='chat/%Y/%m/', blank=True, null=True)

    class Meta:
        verbose_name = 'Mensaje de chat'
        verbose_name_plural = 'Mensajes de chat'
        ordering = ['created_at']

    def __str__(self):
        return f'{self.author}: {self.body[:40]}'
