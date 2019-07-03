# Generated by Django 2.1.2 on 2018-11-06 11:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0005_invoice'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='fees',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AddField(
            model_name='invoice',
            name='local_value',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]