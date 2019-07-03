import requests

from bitnob_utils.exchange_rates import exchange_rate, get_price, exchange_rate_sell
from coin.models import Coin
from wallet.models import Wallet

ONE_BTC = 100000000


def validate_address(address, coin):
    url = 'https://shapeshift.io/validateAddress/' + address + '/' + coin
    res = requests.get(url)
    valid = dict(res.json())
    valid = list(valid.values())
    return valid[0]


def get_fee():
    recommended_fee = 10
    res = requests.get('https://bitcoinfees.earn.com/api/v1/fees/recommended')
    res = dict(res.json())
    if res['fastestFee'] < 60:
        recommended_fee += res['fastestFee']
        return recommended_fee
    else:
        return 25


def to_btc(amount):
    url = 'https://blockchain.info/tobtc?currency=USD&value=' + str(amount)
    res = requests.get(url)
    res = float(res.text)
    # amount = ONE_BTC * res
    return res


def btc_price():
    url = 'https://blockchain.info/ticker'
    response = requests.get(url).json()
    USD_PRICE = response['USD']
    print(print(response['USD']))
    for key, value in USD_PRICE.items():
        if key == '15m':
            return value


def get_account_balance(user_id):
    """
    get the user's wallet
    :param user_id:
    :return: string
    """
    wallet = Wallet.objects.get(user=user_id)
    return wallet.current_balance


def debit_wallet(amount, user_id):
    """
    deduct amount from wallet
    :param amount:
    :param user_id:
    :return: float
    """
    wallet = Wallet.objects.get(user=user_id)
    wallet.current_balance = wallet.current_balance - amount
    wallet.save()
    return wallet.current_balance


def calculate_total_cost(coin, amount, currency, purchase_price, current_price):
    """
    get the price of the coin per USD in local currency

    :return: float
    """
    rate = exchange_rate(coin, currency, purchase_price, current_price)
    btc_price = get_price()
    price_per_btc_dollar = rate / btc_price
    total = amount * price_per_btc_dollar
    return total


def calculate_total_cost_of_purchase(coin, amount, currency, purchase_price, current_price):
    """
    get the price of the coin per USD in local currency

    :return: float
    """
    rate = exchange_rate_sell(coin, currency, purchase_price, current_price)
    btc_price = get_price()
    price_per_btc_dollar = rate / btc_price
    total = amount * price_per_btc_dollar
    return total


def calculate_service_fees(amount):
    """
    calculate the service fee for this transaction
    :param amount:
    :return: fees
    """
    return float(0.02 * amount)


def calculate_difference_from_purchase_price(purchase_price, current_price):
    """
    return the difference between the current selling price and the selling price as at the time of purchase
    :param purchase_price:
    :param current_price:
    :return: float
    """
    # print("$ {0}, ${1}".format(current_price, purchase_price))
    return current_price - purchase_price
