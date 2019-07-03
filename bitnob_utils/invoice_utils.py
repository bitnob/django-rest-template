import urllib.parse
# from urllib import quote
from config.settings.base import env
import requests

url = "https://api.blockchain.info/v2/receive"


def generate_address():
    """
    create a BTC address where the user will send payments to
    :return:
    """
    params = {
        'key': "925a21a1-612d-4557-b558-f26a3f174c74",
        'callback': 'https://5aac81c5.ngrok.io/api/v1/sell/receive_callback',
        'xpub': "xpub6D3YN3BEpWKnm4MWMmYxiJhFoBFhysBsCN6QwNseKSoo6sESTqQiTHb7u6mgPonkVc8r2S2BNxeqgzrqSqRRBay5oVWEMXjyMzMN7g4UYtb"
    }
    wallet_address = requests.get(url, params=params).json()
    get_payment_status(wallet_address['address'])
    return wallet_address['address']


def get_payment_status(address):
    headers = {
        'Content-Type': "text/plain"
    }
    print(address)
    params = {
        'key': "925a21a1-612d-4557-b558-f26a3f174c74",
        'address': address,
        'onNotification': 'KEEP',
        'op': "RECEIVE",
        'confs': 1,
        'callback': 'https://5aac81c5.ngrok.io/api/v1/sell/receive_callback/',
    }
    transaction = requests.post(url + '/balance_update', headers=headers, params=params)
    print(transaction.text)


