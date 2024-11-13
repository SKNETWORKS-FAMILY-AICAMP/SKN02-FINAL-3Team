from logging import setLoggerClass
from select import select

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.conf import settings
from django.utils.log import log_response
from django.views.decorators.csrf import csrf_exempt
from pycparser.c_ast import Continue

from .models import Meeting, Participant, User
from .storage import S3Client
from django.http import JsonResponse, HttpResponse
import os
import json
import markdown
from dotenv import load_dotenv

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny

import requests


def login_view(request):
    return render(request, 'login.html')


def index(request):
    if request.user.is_authenticated:
        user = request.user
        meetings = Meeting.objects.filter(
            participant__user=user).order_by('-started_at').distinct()[:]
        return render(request, 'main.html', {'meetings': meetings, 'user': request.user})
    else:
        return redirect('login')


def meeting_summary(request, meeting_id):
    # 특정 meeting_id의 Meeting 객체 가져오기
    meeting = get_object_or_404(Meeting, pk=meeting_id)
    # 1. 참가자의 user_id 리스트 추출
    participants = Participant.objects.filter(
        meeting=meeting_id).values_list('user_id', flat=True)
    # 2. Checker 역할인 참가자의 user_id 리스트 추출
    checkers_id = Participant.objects.filter(
        meeting_id=meeting_id, is_checker=True).values_list('user_id', flat=True)
    # 3. 모든 참가자의 User 객체 가져오기
    users = User.objects.filter(id__in=participants).values_list(
        'email', flat=True).distinct()  # 중복된 values_list 호출 제거
    # 4. Checker 역할인 참가자의 User 객체 가져오기
    checkerusers = User.objects.filter(id__in=checkers_id).values_list(
        'email', flat=True).distinct()  # 중복된 values_list 호출 제거
    meeting.summary = markdown.markdown(meeting.summary)
    return render(request, 'meeting.html', {
        'meeting': meeting,
        'users': users,
        
    })


def recording_view(request):
    return render(request, 'recording.html')


def detail_view(request, meeting_id):
    # 특정 meeting_id의 Meeting 객체 가져오기
    meeting = get_object_or_404(Meeting, pk=meeting_id)
    # 1. 참가자의 user_id 리스트 추출
    participants = Participant.objects.filter(
        meeting=meeting_id).values_list('user_id', flat=True)
    # 2. Checker 역할인 참가자의 user_id 리스트 추출
    checkers_id = Participant.objects.filter(
        meeting_id=meeting_id, is_checker=True).values_list('user_id', flat=True)
    # 3. 모든 참가자의 User 객체 가져오기
    users = User.objects.filter(id__in=participants).values_list(
        'email', flat=True).distinct()  # 중복된 values_list 호출 제거

    # 4. Checker 역할인 참가자의 User 객체 가져오기

    checkerusers = User.objects.filter(id__in=checkers_id).values_list(
        'email', flat=True).distinct()  # 중복된 values_list 호출 제거
    if meeting.content == None:
        sorted_speakers = []
    else:
        speakers_list = list({context['speaker']
                             for context in meeting.content['minutes']})
        sorted_speakers = sorted(speakers_list)
        if "Unknown" in sorted_speakers:
            sorted_speakers.remove("Unknown")
        elif "알 수 없음" in sorted_speakers:
            sorted_speakers.remove("알 수 없음")

    return render(request, 'meeting_detail.html', {
        'meeting': meeting,
        'users': users,
        'speakers': sorted_speakers
    })


def speaker_modify(request):
    if request.method == 'POST':
        meeting = Meeting.objects.get(pk=request.POST['meeting_id'])
        selected_values_str= request.POST.get('selected_speakers')
        selected_values = json.loads(selected_values_str) # 선택된 값을 배열로 가져옴

        if "Unknown" in selected_values:
            selected_values.remove("Unknown")
        elif "알 수 없음" in selected_values:
            selected_values.remove("알 수 없음")

        # 이메일 주소에 맞는 사용자 검색 및 이름 리스트에 추가
        user_name_list = []
        for speaker in selected_values:
            user = User.objects.filter(email=speaker)
            # QuerySet에서 이름을 추출하여 리스트에 추가
            for user in user.values_list('last_name', 'first_name'):
                user_name_list.append(f"{user[0]}{user[1]}")  # 성과 이름을 결합하여 추가
        print(type(selected_values),selected_values)
        print(user_name_list)
        speakers_list = list({context['speaker'] for context in meeting.content['minutes']})
        sorted_speakers = sorted(speakers_list)
        print(sorted_speakers) #해결
        if "Unknown" in sorted_speakers:
            sorted_speakers.remove("Unknown")
        
        if "unknown" in sorted_speakers:
            sorted_speakers.remove("unknown")

        elif "알 수 없음" in sorted_speakers:
            sorted_speakers.remove("알 수 없음")
        print(sorted_speakers) # 해결

        for context in meeting.content['minutes']:
            speaker = context["speaker"]
            if speaker == "Unknown" or speaker == "알 수 없음" : continue

            idx = sorted_speakers.index(speaker)
            print(idx, speaker)
            new_speaker = user_name_list[idx]
            print(new_speaker)
            context["speaker"] = new_speaker

        meeting.save()

        return JsonResponse({'message': selected_values}, status=200)
    return JsonResponse({'error': 'Invalid request'}, status=400)


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
        else:
            host_id = request.user.id
            meeting = Meeting.objects.create(
                title=title,
                started_at=started_at,
                ended_at=ended_at,
                host_id=host_id,
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
            s3_client.upload(file=audio_file, file_name=filename,
                             bucket_name=bucket_name)

            # Meeting 객체에 S3 경로 저장
            meeting = Meeting.objects.get(id=meeting.id)
            meeting.file_path = s3_file_path  # S3 파일 경로를 DB에 저장
            meeting.save()

            user_email = request.user.email

            attendees = request.POST.getlist('attendees[]')  # 리스트로 받음
            if user_email not in attendees:
                attendees.append(user_email)
            print(attendees)
            s3_file_path = settings.AWS_S3_CUSTOM_DOMAIN + '/' + s3_file_path
            print(s3_file_path)

            # 모델 서버에 전송
            url = str(os.getenv('MODEL_SERVER_URL'))
            payload = {
                "meeting_id": meeting.id,
                "audio_url": s3_file_path,
                "num_of_person": len(attendees),
            }
            headers = {
                'Content-Type': 'application/json',
                # 필요한 경우 CSRF 토큰이나 인증 헤더 추가
            }
            try:

                response = requests.post(url, json=payload, headers=headers)
                response.raise_for_status()  # 요청이 성공했는지 확인

            except requests.exceptions.RequestException as e:
                print(f"POST 요청 중 오류 발생: {e}")


            for attendee in attendees:
                Participant.objects.create(
                    meeting=meeting, is_checker=False, created_at=meeting.started_at, user=User.objects.get(email=attendee))

            return JsonResponse({'message': 'File uploaded successfully'}, status=200)

    return JsonResponse({'error': 'Invalid request'}, status=400)


load_dotenv()

API_KEY = os.getenv('API_KEY')


def verify_api_key(request):
    api_key = request.data['api_key']
    return api_key == API_KEY


@api_view(['PATCH'])
@permission_classes([AllowAny])
@csrf_exempt
def store_meeting_detail(request):
    if not verify_api_key(request):
        return Response({'error': 'Forbidden: Invalid API Key'}, status=403)

    meeting_id = request.data['meeting_id']
    meeting = Meeting.objects.get(id=meeting_id)
    meeting.content = request.data['content']
    meeting.save()

    return Response({'message': 'Meeting detail updated successfully'}, status=200)


@api_view(['PATCH'])
@permission_classes([AllowAny])
@csrf_exempt
def store_meeting_summary(request):
    if not verify_api_key(request):
        return Response({'error': 'Forbidden: Invalid API Key'}, status=403)

    meeting_id = request.data['meeting_id']
    meeting = Meeting.objects.get(id=meeting_id)
    meeting.summary = request.data['summary']
    meeting.save()

    return Response({'message': 'Meeting summary updated successfully'}, status=200)


@csrf_exempt  # CSRF 검증을 우회합니다. 보안상 주의 필요
def search_meetings(request):
    user = request.user
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            search_type = data.get('search_type')
            query = data.get('query')

            if not search_type or not query:
                return JsonResponse({'error': 'Invalid parameters'}, status=400)

            if search_type == 'title':
                meetings = Meeting.objects.filter(
                    title__icontains=query, participant__user=user)
            elif search_type == 'author':
                meetings = Meeting.objects.filter(
                    host__email__icontains=query, participant__user=user)
            else:
                return JsonResponse({'error': 'Invalid search type'}, status=400)

            # 검색 결과 직렬화
            meetings_data = []
            for meeting in meetings:
                meetings_data.append({
                    'id': meeting.id,
                    'title': meeting.title,
                    'author': meeting.host.username,
                    'started_at': meeting.started_at.strftime('%Y-%m-%d %H:%M'),
                    'summary': meeting.summary,
                })

            return JsonResponse({'meetings': meetings_data}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)