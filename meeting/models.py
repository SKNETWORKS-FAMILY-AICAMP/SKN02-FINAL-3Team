from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class Department(models.Model):
    department_code = models.CharField(max_length=10, primary_key=True)
    department_name = models.CharField(max_length=100)

    def __str__(self):
        return self.department_name


class Position(models.Model):
    position_code = models.CharField(max_length=10, primary_key=True)
    position_name = models.CharField(max_length=100)

    def __str__(self):
        return self.position_name


class MemberManager(BaseUserManager):
    def create_user(self, id, password=None, **extra_fields):
        if not id:
            raise ValueError('The ID field must be set')
        user = self.model(id=id, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, id, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        # # 기본 부서와 직위 설정 (필요에 따라 수정)
        # if 'department_code' not in extra_fields:
        #     # 첫 번째 부서 사용
        #     extra_fields['department_code'] = Department.objects.first()
        # else:
        #     extra_fields['department_code'] = Department.objects.get(
        #         department_code=extra_fields['department_code'])

        # if 'position' not in extra_fields:
        #     extra_fields['position'] = Position.objects.first()  # 첫 번째 직위 사용
        # else:
        #     extra_fields['position'] = Position.objects.get(
        #         position_code=extra_fields['position'])
        extra_fields['department_code'] = Department.objects.get(
            department_code=extra_fields['department_code'])

        extra_fields['position'] = Position.objects.get(
            position_code=extra_fields['position'])

        return self.create_user(id, password, **extra_fields)


class Member(AbstractBaseUser, PermissionsMixin):
    id = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=100)
    department_code = models.ForeignKey(
        'Department', db_column='department_code', on_delete=models.CASCADE)
    position = models.ForeignKey('Position', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = MemberManager()

    USERNAME_FIELD = 'id'
    REQUIRED_FIELDS = ['name', 'department_code', 'position']

    def __str__(self):
        return self.name


class Meeting(models.Model):
    meeting_id = models.AutoField(primary_key=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    meeting_title = models.CharField(max_length=200)
    meeting_content = models.TextField()
    meeting_date = models.DateField(default=timezone.now)

    def __str__(self):
        return self.meeting_title
