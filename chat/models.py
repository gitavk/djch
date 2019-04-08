from django.db import models
from django.conf import settings

from .manager import ThreadManager


class Thread(models.Model):
    first = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chat_thread_first'
    )
    second = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chat_thread_second'
    )
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = ThreadManager()

    def __str__(self):
        return f'{self.id}'

    @property
    def room_group_name(self):
        return f'chat_{self.id}'

    def broadcast(self, msg=None):
        if msg is not None:
            broadcast_msg_to_chat(msg, group_name=self.room_group_name, user='admin')
            return True
        return False


class ChatMessage(models.Model):
    thread = models.ForeignKey(Thread, null=True, blank=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='sender',
        on_delete=models.CASCADE
    )
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.id}'
