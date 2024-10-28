from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .models import Meeting, Participant
from django.http import JsonResponse
import os

def login_view(request):
    return render(request, 'login.html')

def index(request):
    print(request)
    if request.user.is_authenticated:
        meetings = Meeting.objects.all().order_by('-started_at')[:15]
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
        # 빈 Meeting 객체를 생성하여 저장하고 id를 자동 생성
        meeting = Meeting.objects.create()  # 기본 값으로 빈 Meeting 객체 생성

        # 파일 이름
        filename = f"{meeting.id}.wav"
        # 파일 경로 설정
        file_path = os.path.join(RECORD_DIR, filename)
        audio_file = request.FILES['audio']

        # 해당 폴더가 없다면 생성
        if not os.path.exists(RECORD_DIR):
            os.makedirs(RECORD_DIR)
        # 파일 저장
        with open(file_path, 'wb+') as destination:
            for chunk in audio_file.chunks():
                destination.write(chunk)

        # db 저장
        meeting.started_at = request.POST['startTime']
        meeting.ended_at = request.POST['endTime']
        meeting.title = request.POST.get('meetingName')
        meeting.host_id = request.user
        print(meeting)
        meeting.save()


        attendees = request.POST.getlist('attendees[]') # 리스트로 받음
        checkers = request.POST.getlist('checkers[]')
        for attendee in attendees:
            for checker in checkers:
                if checker == attendee :
                    Participant.objects.create(meeting=meeting, attendee=attendee, is_checker=True, created_at=meeting.started_at)
                else :
                    Participant.objects.create(meeting=meeting, attendee=attendee, is_checker=False, created_at=meeting.started_at)



        return JsonResponse({'message': 'File uploaded successfully'}, status=200)

    return JsonResponse({'error': 'Invalid request'}, status=400)


## error 처리
# 400, 404,500은 handler로 처리
# 401 Unauthorized (일반적으로 직접 핸들링 필요)
def unauthorized(request):
    return render(
        request,
        'error.html',
        {'error_code': 401, 'error_message': "Authorization Failed"},
        status=401)
