from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import Meeting, Participant


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


def login_view(request):
    return render(request, 'login.html')
