# Generated by Django 2.1.2 on 2018-11-02 12:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('coin', '0003_auto_20181017_1202'),
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SellOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('value', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('fee', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('address', models.CharField(max_length=256)),
                ('transaction_id', models.CharField(max_length=256, null=True)),
                ('reference_id', models.CharField(max_length=256, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified_on', models.DateTimeField(auto_now=True)),
                ('coin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sell_coin', to='coin.Coin')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sellorder_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
