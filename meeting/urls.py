from django.urls import path, include
from django.shortcuts import redirect
from . import views
from .views import save_audio

urlpatterns = [
    path('', lambda request: redirect('login/')),
    path('login/', views.login_view),
    path('main/', views.index, name='main'),
    # index 뷰가 main.html을 렌더링합니다.
    path('recording/', views.recording_view, name='recording'),
    path('meeting_summary/<int:meeting_id>/',
         views.meeting_summary, name='meeting_summary'),
    path('save_audio', views.save_audio, name='save_audio'),
]
