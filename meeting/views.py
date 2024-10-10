from .models import Member
from django.shortcuts import render, redirect
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib import messages
# Create your views here.


def index(request):
    session_data = {"username": request.session['username'],
                    "department": request.session['department'],
                    "position": request.session['position']}
    return render(request, 'main.html', {'session_data': session_data})


def login_view(request):
    if request.method == 'POST':
        user_id = request.POST['id']
        password = request.POST['password']
        user = authenticate(request, username=user_id, password=password)
        if user is not None:
            login(request, user)
            request.session['username'] = user.name  # 사용자 이름을 세션에 저장
            # 부서 이름을 세션에 저장
            request.session['department'] = user.department_code.department_name
            request.session['position'] = user.position.position_name
            return redirect('main')  # 'main'은 main.html을 렌더링하는 URL의 이름입니다.
        else:
            messages.error(request, '아이디 또는 비밀번호가 틀렸습니다.')
    return render(request, 'login.html')
