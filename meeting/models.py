from django.db import models
import os


class Post(models.Model):
    title = models.CharField(max_length=30)
    hook_text = models.TextField(max_length=100, blank=True)
    content = models.TextField()
