# Generated by Django 2.1.2 on 2018-10-21 12:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('level', '0006_auto_20181021_0049'),
    ]

    operations = [
        migrations.AlterField(
            model_name='levelupgraderequest',
            name='approved',
            field=models.BooleanField(default=False),
        ),
    ]