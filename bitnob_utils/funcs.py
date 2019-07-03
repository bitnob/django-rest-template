import requests
from random import randint
from django.conf import settings


def send_hubtel_sms(phone_number, sms_code):
    url = 'http://cheapglobalsms.com/api_v1'
    params = {
        'sub_account': '2132_bitcoin',
        'sub_account_pass': 'diamond',
        'action': 'send_sms',
        'route': 1,
        'sender_id': 'Diamond',
        'recipients': phone_number,
        'message': sms_code
    }
    send_sms = requests.post(url, params=params)
    print(send_sms.text)
    return send_sms.text


def send_hubtel_sms(phone_number, sms_code):
    url = "https://api.hubtel.com/v1/messages/send"
    params = {
        "From": "Bitnob",
        "To": phone_number,
        "Content": sms_code,
        "ClientId": "",
        "ClientSecret": "",
        "RegisteredDelivery": ""
    }
    send_sms = requests.post(url, params=params)
    print(send_sms.text)
    return send_sms.text


def verify_bank_account(account_number, bankcode):
    url = 'https://gwot5erqucxr9jlrx-mock.stoplight-proxy.io/api/acctinq/wrapper'
    params = {
        'bankcode': bankcode,
        'accountnumber': account_number,
        'api_key': 'HKJbdbkdskbLHlvLvcsljljjhjhvjvJjJJHjbljvjv'
    }

    send_request = requests.get(url, params)
    print(send_request.text)
    return send_request.text


def validate_pin(pin):
    headers = {'content-type': 'application/json'}
    data = {
        "pin": pin
    }
    response = requests.post(settings.VOUCHER_API + 'validate_voucher_pub/', params=data, headers=headers)
    print(response.status_code)
    if response.status_code == 400:
        print(response.status_code)
        return False

    if response.status_code == 200:
        return response.json()


def change_voucher_status(pin):
    headers = {'content-type': 'application/json'}
    data = {
        "pin": pin
    }
    response = requests.post(settings.VOUCHER_API + 'change_voucher_status/', params=data, headers=headers)
    print(response.text)
    if response.status_code == 200:
        return True
    else:
        return False
