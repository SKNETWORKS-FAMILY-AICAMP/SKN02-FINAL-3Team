from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from pycparser.c_ast import Continue

from .models import Meeting, Participant, User
from .storage import S3Client
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
    # 특정 meeting_id의 Meeting 객체 가져오기
    meeting = get_object_or_404(Meeting, pk=meeting_id)
    # 1. 참가자의 user_id 리스트 추출
    participants = Participant.objects.filter(meeting=meeting_id).values_list('user_id', flat=True)
    # 2. Checker 역할인 참가자의 user_id 리스트 추출
    checkers_id = Participant.objects.filter(meeting_id=meeting_id, is_checker=True).values_list('user_id', flat=True)
    # 3. 모든 참가자의 User 객체 가져오기
    users = User.objects.filter(id__in=participants).values_list('email', flat=True).distinct()  # 중복된 values_list 호출 제거
    # 4. Checker 역할인 참가자의 User 객체 가져오기
    checkerusers = User.objects.filter(id__in=checkers_id).values_list('email', flat=True).distinct() # 중복된 values_list 호출 제거

    return render(request, 'meeting.html', {
        'meeting': meeting,
        'users': users,
        'checkerusers': checkerusers
    })

def recording_view(request):
    return render(request, 'recording.html')


def detail_view(request, meeting_id):
    # 특정 meeting_id의 Meeting 객체 가져오기
    meeting = get_object_or_404(Meeting, pk=meeting_id)
    # 1. 참가자의 user_id 리스트 추출
    participants = Participant.objects.filter(meeting=meeting_id).values_list('user_id', flat=True)
    # 2. Checker 역할인 참가자의 user_id 리스트 추출
    checkers_id = Participant.objects.filter(meeting_id=meeting_id, is_checker=True).values_list('user_id', flat=True)
    # 3. 모든 참가자의 User 객체 가져오기
    users = User.objects.filter(id__in=participants).values_list('email', flat=True).distinct()  # 중복된 values_list 호출 제거
    # 4. Checker 역할인 참가자의 User 객체 가져오기
    checkerusers = User.objects.filter(id__in=checkers_id).values_list('email', flat=True).distinct()  # 중복된 values_list 호출 제거

    return render(request, 'meeting_detail.html', {
        'meeting': meeting,
        'users': users,
        'checkerusers': checkerusers
    })

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

            # S3Client 인스턴스 생성 (환경 변수 또는 settings에서 AWS 자격 증명 가져오기)
            s3_client = S3Client(
                AWS_ACCESS_KEY_ID=settings.AWS_ACCESS_KEY_ID,
                AWS_SECRET_ACCESS_KEY=settings.AWS_SECRET_ACCESS_KEY
            )

            # S3 버킷 이름 (settings.py에 저장되어 있다고 가정)
            bucket_name = settings.AWS_STORAGE_BUCKET_NAME

            # 파일 이름과 S3 경로 설정
            filename = f"{meeting.id}.wav"
            s3_file_path = os.path.join(s3_client.base, filename)

            # 업로드할 파일 가져오기
            audio_file = request.FILES['audio']

            # 파일을 S3에 업로드하고, 업로드된 S3 경로를 DB에 저장
            result = s3_client.upload(file=audio_file, file_name=filename, bucket_name=bucket_name)
            print(result)

            # Meeting 객체에 S3 경로 저장
            meeting = Meeting.objects.get(id=meeting.id)
            meeting.file_path = s3_file_path  # S3 파일 경로를 DB에 저장
            meeting._do_update()

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

