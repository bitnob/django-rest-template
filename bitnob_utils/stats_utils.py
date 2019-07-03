from django.utils.timezone import make_aware

from wallet.models import Deposit
from django.db.models import Sum, Aggregate, Avg, Count
from datetime import datetime, timedelta

today = make_aware(datetime.today())
yesterday = today - timedelta(days=1)
last_month = today - timedelta(days=30)
last_week = today - timedelta(days=7)
last_year = today - timedelta(days=365)
