# Generated by Django 2.1.2 on 2018-12-05 18:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_auto_20181126_1304'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userdata',
            name='govt_id',
            field=models.CharField(max_length=400, null=True),
        ),
        migrations.AlterField(
            model_name='userdata',
            name='selfie',
            field=models.CharField(max_length=400, null=True),
        ),
        migrations.AlterField(
            model_name='userdata',
            name='social_account',
            field=models.URLField(max_length=400, null=True),
        ),
        migrations.AlterField(
            model_name='userdata',
            name='utility_bill',
            field=models.CharField(max_length=400, null=True),
        ),
    ]
