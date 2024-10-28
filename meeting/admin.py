from django.contrib import admin
from .models import Meeting, Participant, Notification

admin.site.register(Meeting)
admin.site.register(Participant)

admin.site.register(Notification)
