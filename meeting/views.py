from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .models import Meeting, Participant
from django.http import JsonResponse
import os

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
def save_audio(request):
    if request.method == 'POST':
        audio_file = request.FILES['audio']
        meeting_name = request.POST.get('meeting_name')  # 기본 이름 설정

        folder = 'record'  # 저장할 폴더
        filename = f"{meeting_name}.wav"

        # 해당 폴더가 없다면 생성
        if not os.path.exists(folder):
            os.makedirs(folder)

        # 파일 경로 설정
        file_path = os.path.join(folder, filename)

        # 파일 저장
        with open(file_path, 'wb+') as destination:
            for chunk in audio_file.chunks():
                destination.write(chunk)

        return JsonResponse({'message': 'File uploaded successfully'}, status=200)

    return JsonResponse({'error': 'Invalid request'}, status=400)

