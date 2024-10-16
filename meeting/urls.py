from django.urls import path, include
from . import views

urlpatterns = [
    path('login/', views.login_view),
    path('main/', views.index, name='main'),
    # index 뷰가 main.html을 렌더링합니다.
    path('recording/', views.recording_view, name='recording'),
    path('recording/save/', views.save_recording_view, name='save_recording'),
    path('meeting_summary/<int:meeting_id>/',
         views.meeting_summary, name='meeting_summary'),
]
