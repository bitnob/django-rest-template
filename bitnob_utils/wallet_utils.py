from django.utils.timezone import make_aware

from wallet.models import Deposit
from django.db.models import Sum, Aggregate, Avg, Count
from datetime import datetime, timedelta

today = make_aware(datetime.today())
yesterday = today - timedelta(days=1)
last_month = today - timedelta(days=30)
last_week = today - timedelta(days=7)


def total_deposits(wallet_id):
    """
    sum of all the completed deposits by the user
    :param wallet_id
    :return: total deposits
    """
    return list(Deposit.objects.filter(wallet=wallet_id).aggregate(Sum('value')).values())[0] or 0.00


def monthly_total(wallet_id):
    """
    sum of all the completed deposits by the user in the last 30 days
    :param wallet_id
    :return: total deposits
    """
    return list(Deposit.objects.filter(wallet=wallet_id)
                .filter(created_at__gte=last_month)
                .aggregate(Sum('value')).values())[0] or 0.00


def daily_total(wallet_id):
    """
    sum of all the completed deposits by the user in the last 24hrs
    :param wallet_id
    :return: total deposits
    """
    return list(Deposit.objects.filter(wallet=wallet_id).filter(created_at__gte=yesterday)
                .aggregate(Sum('value'))
                .values())[0] or 0.00


def weekly_total(wallet_id):
    """
    sum of all the completed deposits by the user in the last 7 days
    :param wallet_id
    :return: total deposits
    """
    return list(Deposit.objects.filter(wallet=wallet_id).filter(created_at__gte=last_week)
                .aggregate(Sum('value'))
                .values())[0] or 0.00


def has_exceeded_limit(wallet_id, limit, amount):
    """
    if the user has exceeded their limit, prevent them from making additional deposits
    :param wallet_id:
    :param limit:
    :param amount:
    :return:
    """
    total_deposit = monthly_total(wallet_id)
    return False if total_deposit + amount < limit else True


