from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages

import os
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Meeting, Participant

# Create your views here.


def login_view(request):
    return render(request, 'login.html')


def index(request):
    if request.user.is_authenticated:
        participant_meetings = Participant.objects.filter(
            user=request.user).values_list('meeting', flat=True)
        meetings = Meeting.objects.filter(
            id__in=participant_meetings).order_by('-started_at')[:15]
        return render(request, 'main.html', {'meetings': meetings, 'user': request.user})
    else:
        return redirect('login')


def meeting_summary(request, meeting_id):
    meeting = get_object_or_404(Meeting, pk=meeting_id)
    Participants = Participant.objects.filter(meeting=meeting)
    return render(request, 'meeting.html', {'meeting': meeting, 'Participants': Participants})


def recording_view(request):
    return render(request, 'recording.html')


# 상대 경로 설정
RECORD_DIR = os.path.join(settings.BASE_DIR, 'record')


@csrf_exempt
def save_recording_view(request):
    print(request)
    if request.method == 'POST' and 'audio' in request.FILES:
        audio_file = request.FILES['audio']

        # 파일 저장 경로 설정
        if not os.path.exists(RECORD_DIR):
            os.makedirs(RECORD_DIR)

        # 파일 저장
        file_path = os.path.join(RECORD_DIR, audio_file.name)
        with open(file_path, 'wb') as f:
            for chunk in audio_file.chunks():
                f.write(chunk)

    return render(request, 'recording2.html')
