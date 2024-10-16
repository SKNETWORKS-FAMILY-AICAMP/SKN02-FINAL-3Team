from django.contrib import admin
from .models import Meeting, Minutes, Participant, Confirmation, Notification

admin.site.register(Meeting)
admin.site.register(Minutes)
admin.site.register(Participant)
admin.site.register(Confirmation)
admin.site.register(Notification)
