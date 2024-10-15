from django.urls import path, include
from . import views

urlpatterns = [
    path('login/', views.login_view),
    path('main/', views.index, name='main'),  # index 뷰가 main.html을 렌더링합니다.
    path('meeting/<int:meeting_id>/summary/', views.meeting_summary,
         name='meeting_summary'),  # 추가된 URL 패턴
]
