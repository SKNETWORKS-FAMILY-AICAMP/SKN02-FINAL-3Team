from django.shortcuts import render, redirect
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib import messages
# Create your views here.


def index(request):

    return render(request, 'main.html')


def login_view(request):
    return render(request, 'login.html')
