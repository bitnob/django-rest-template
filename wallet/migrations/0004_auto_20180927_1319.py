# Generated by Django 2.1.1 on 2018-09-27 13:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0003_auto_20180927_1310'),
    ]

    operations = [
        migrations.AlterField(
            model_name='manualdeposit',
            name='ref_code',
            field=models.CharField(editable=False, max_length=10),
        ),
    ]
