from django.contrib import admin
from .models import Department, Position, Member, Meeting
from django import forms
from django.contrib.auth.hashers import make_password

admin.site.register(Department)
admin.site.register(Position)


class MemberAdminForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = '__all__'
        widgets = {
            'password': forms.PasswordInput(render_value=True),
        }


class MemberAdmin(admin.ModelAdmin):
    form = MemberAdminForm

    def save_model(self, request, obj, form, change):
        if form.cleaned_data['password']:
            obj.password = make_password(form.cleaned_data['password'])
        super().save_model(request, obj, form, change)


admin.site.register(Member, MemberAdmin)


class MeetingAdmin(admin.ModelAdmin):
    readonly_fields = ('meeting_date',)


admin.site.register(Meeting, MeetingAdmin)
