# Generated by Django 2.0.8 on 2018-08-10 07:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('country', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='country',
            name='tel_code',
            field=models.CharField(default=None, max_length=3, unique=True),
        ),
    ]