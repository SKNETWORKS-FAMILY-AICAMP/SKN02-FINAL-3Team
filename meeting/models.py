from django.db import models
import os
from django.utils import timezone
from django.contrib.auth.models import User


class Meeting(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    started_at = models.DateTimeField(default=timezone.now)
    ended_at = models.DateTimeField(default=timezone.now)
    file_path = models.FileField(upload_to='recordings/')
    host = models.ForeignKey(User, on_delete=models.CASCADE)
    summary = models.TextField()
    content = models.TextField()

    def __str__(self):
        return str(self.id)


class Participant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)
    is_checker = models.BooleanField(default=False)
    is_confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.user)


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    id = models.AutoField(primary_key=True)
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.content


# USER table - Django에서 자동 생성
