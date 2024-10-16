from django.db import models
import os
from django.utils import timezone
from django.contrib.auth.models import User


class Recording(models.Model):
    file_path = models.FileField(upload_to='recordings/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Recording at {self.created_at}'


class Meeting(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    started_at = models.DateTimeField(default=timezone.now)
    ended_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    host = models.ForeignKey(User, on_delete=models.CASCADE)
    summary = models.TextField()

    def __str__(self):
        return self.title


class Minutes(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)
    content = models.TextField()

    def __str__(self):
        return self.content


class Participant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)
    is_checker = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class Confirmation(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return self.participant.user.username


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    id = models.AutoField(primary_key=True)
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.content
