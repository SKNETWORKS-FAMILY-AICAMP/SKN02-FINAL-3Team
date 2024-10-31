from django.urls import path
from django.shortcuts import redirect
from . import views
from django.conf.urls import handler400, handler403, handler404, handler500

urlpatterns = [
    path('', lambda request: redirect('login/')),
    path('login/', views.login_view),
    # index 뷰가 main.html을 렌더링합니다.
    path('main/', views.index, name='main'),
    path('recording/', views.recording_view, name='recording'),
    path('meeting_summary/<int:meeting_id>/',
         views.meeting_summary, name='meeting_summary'),
    path('save_audio', views.save_audio, name='save_audio'),
    path('meeting/detail', views.store_meeting_detail,
         name='store_meeting_detail'),
    path('meeting/summary', views.store_meeting_summary,
         name='store_meeting_summary'),
]

handler400 = "meeting.views.bad_request"
handler404 = "views.page_not_found"
handler500 = "meeting.views.server_error"
