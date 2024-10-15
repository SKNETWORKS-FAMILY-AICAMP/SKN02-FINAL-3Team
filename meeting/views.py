from django.shortcuts import render, redirect
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib import messages

import os
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Recording

# Create your views here.


def index(request):
    return render(request, 'main.html')

def login_view(request):
    return render(request, 'login.html')

def recording_view(request):
    return render(request, 'recording.html')

# 상대 경로 설정
RECORD_DIR = os.path.join(settings.BASE_DIR, 'record')

@csrf_exempt
def save_recording_view(request):
    if request.method == 'POST' and 'audio' in request.FILES:
        audio_file = request.FILES['audio']

        # 파일 저장 경로 설정
        if not os.path.exists(RECORD_DIR):
            os.makedirs(RECORD_DIR)

        file_path = os.path.join(RECORD_DIR, audio_file.name)
    return render(request, 'recording2.html')
