# Generated by Django 2.1.2 on 2019-01-08 14:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('level', '0010_levelupgraderequest_current_level'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='levelupgraderequest',
            name='current_level',
        ),
    ]
