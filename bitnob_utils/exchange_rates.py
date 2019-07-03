import requests
from django.conf import settings


def get_price():
    """
    bitpay API https://bitpay.com/exchange-rates
    :return:
    """
    response = requests.get(settings.RATES_API + '/BTC/USD').json()
    return response['rate']


# def get_price():
#     url = 'https://blockchain.info/ticker'
#     response = requests.get(url).json()
#     USD_PRICE = response['USD']
#     # print(print(response['USD']))
#     for key, value in USD_PRICE.items():
#         if key == '15m':
#             return value


def exchange_rate(coin, currency_code, purchase_price, current_price):
    """
    Exchange rate from USD to Local currency of the User
    :param coin:
    :param purchase_price:
    :param current_price:
    :param currency_code:
    :return:
    """
    response = requests.get(settings.RATES_API + '/' + coin + '/' + currency_code).json()
    percentage_gain_loss = calculate_premium(float(purchase_price), current_price)
    base_premium = 0.03
    premium = 0.05 if percentage_gain_loss > -0.05 else base_premium
    add_premium = premium * response['rate']
    rate = add_premium + response['rate']
    return rate


def exchange_rate_sell(coin, currency_code, purchase_price, current_price):
    """
    Exchange rate from USD to Local currency of the User
    :param coin:
    :param purchase_price:
    :param current_price:
    :param currency_code:
    :return:
    """
    response = requests.get(settings.RATES_API + '/' + coin + '/' + currency_code).json()
    percentage_gain_loss = calculate_premium(float(purchase_price), current_price)
    base_premium = 0.03
    premium = 0.05 if percentage_gain_loss > -0.05 else base_premium
    premium = premium * response['rate']
    rate = response['rate'] - premium
    return rate


def calculate_premium(purchase_price, current_price):
    """
    Calculate the premium by automatically adjusting the selling price based on the market conditions
    :param purchase_price:
    :param current_price:
    :return: premium

    TODO: handle Division by 0
    """
    return (current_price - purchase_price) / purchase_price


