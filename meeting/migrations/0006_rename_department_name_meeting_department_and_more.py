# Generated by Django 5.1.1 on 2024-10-10 05:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meeting', '0005_rename_department_name_member_department_code_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='meeting',
            old_name='department_name',
            new_name='department',
        ),
        migrations.RenameField(
            model_name='member',
            old_name='position_code',
            new_name='position',
        ),
    ]
