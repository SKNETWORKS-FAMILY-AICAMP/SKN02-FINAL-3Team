from django.test import TestCase
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from pycparser.c_ast import Continue

from .models import Meeting, Participant, User
from .storage import S3Client
from django.http import JsonResponse
import os

meeting_id = 26
meeting = Meeting.objects.get(pk=meeting_id)
# 1. 참가자의 user_id 리스트 추출
participants = Participant.objects.filter(meeting=meeting_id).values_list('user_id', flat=True)
# 2. Checker 역할인 참가자의 user_id 리스트 추출
checkers_id = Participant.objects.filter(meeting_id=meeting_id, is_checker=True).values_list('user_id', flat=True)
# 3. 모든 참가자의 User 객체 가져오기
users = User.objects.filter(id__in=participants).values_list('email', flat=True).distinct()  # 중복된 values_list 호출 제거
print(users.count())
# 4. Checker 역할인 참가자의 User 객체 가져오기
checkerusers = User.objects.filter(id__in=checkers_id).values_list('email', flat=True).distinct()


# #json speaker 가져오기
speakers_list = list({context['speaker'] for context in meeting.content['minutes']})
sorted_speakers = sorted(speakers_list)
sorted_speakers.remove("알 수 없음")
print(sorted_speakers)

# Create your tests here.
