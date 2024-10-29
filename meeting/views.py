from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from pycparser.c_ast import Continue

from .models import Meeting, Participant, User
from django.http import JsonResponse
import os


def login_view(request):
    return render(request, 'login.html')


def index(request):
    if request.user.is_authenticated:
        host_id = request.user.id
        meetings = Meeting.objects.filter(
            host_id=host_id).order_by('-started_at')[:15]
        return render(request, 'main.html', {'meetings': meetings, 'user': request.user})
    else:
        return redirect('login')


def meeting_summary(request, meeting_id):
    meeting = get_object_or_404(Meeting, pk=meeting_id)
    Participants = Participant.objects.filter(meeting_id=meeting)
    return render(request, 'meeting.html', {'meeting': meeting, 'Participants': Participants})


def recording_view(request):
    return render(request, 'recording.html')


# 상대 경로 설정
RECORD_DIR = os.path.join(settings.BASE_DIR, 'record')


@csrf_exempt
def save_audio(request):
    if request.method == 'POST':

        # db 저장
        started_at = request.POST['startTime']
        ended_at = request.POST['endTime']
        title = request.POST.get('meetingName')
        if title == "":
            return render(request, '401.html', status=401)
        else :
            host_id = request.user.id
            meeting = Meeting.objects.create(
                title = title,
                started_at = started_at,
                ended_at = ended_at,
                host_id = host_id,
            )

            # 파일 이름
            filename = f"{meeting.id}.wav"
            # 파일 경로 설정
            file_path = os.path.join(RECORD_DIR, filename)
            audio_file = request.FILES['audio']
            meeting.file_path = file_path
            meeting.save()

            # 해당 폴더가 없다면 생성
            if not os.path.exists(RECORD_DIR):
                os.makedirs(RECORD_DIR)
            # 파일 저장
            with open(file_path, 'wb+') as destination:
                for chunk in audio_file.chunks():
                    destination.write(chunk)

            user_email = request.user.email
            attendees = request.POST.getlist('attendees[]') # 리스트로 받음
            if user_email not in attendees:
                attendees.append(user_email)

            print(attendees)
            checkers = request.POST.getlist('checkers[]')
            print(checkers)
            for attendee in attendees:
                for checker in checkers:
                    if checker == attendee :
                        Participant.objects.create(meeting=meeting, is_checker=True, created_at=meeting.started_at, user=User.objects.get(email=attendee))
                    elif checker != attendee :
                        Participant.objects.create(meeting=meeting, is_checker=False, created_at=meeting.started_at, user=User.objects.get(email=attendee))
                    else :
                        continue


            return JsonResponse({'message': 'File uploaded successfully'}, status=200)

    return JsonResponse({'error': 'Invalid request'}, status=400)


# error 처리
# 400, 404,500은 handler로 처리
# 401 Unauthorized (일반적으로 직접 핸들링 필요)
def unauthorized(request):
    return render(
        request,
        'error.html',
        {'error_code': 401, 'error_message': "Authorization Failed"},
        status=401)
