from django import forms
from .models import Meeting

class MeetingForm(forms.ModelForm):
    class Meta:
        model = Meeting
        fields = ['title']  # title 필드만 포함
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '제목 입력'}),
        }
