# Generated by Django 5.1.1 on 2024-10-10 06:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meeting', '0007_alter_member_department_code'),
    ]

    operations = [
        migrations.RenameField(
            model_name='member',
            old_name='department_code',
            new_name='department',
        ),
    ]
