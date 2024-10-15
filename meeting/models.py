from django.db import models
import os

class Recording(models.Model):
    file_path = models.FileField(upload_to='recordings/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Recording at {self.created_at}'