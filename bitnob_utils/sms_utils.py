import requests

send_url = "https://api.authy.com/protected/json/phones/verification/start"
verify_url = "https://api.authy.com/protected/json/phones/verification/check"
headers = {
    "X-Authy-API-Key": "fgxJa6CpKdosDzvQExWsy6LM5v3yqhtW"
}


def send_code(phone_number, country_code):
    """
    verify a user's phone number using twilio 2FA by sending a code to the phone number
    :param phone_number:
    :param country_code:
    :return: Boolean
    """
    params = {
        'via': 'sms',
        'phone_number': phone_number,
        'country_code': country_code
    }
    response = requests.post(send_url, params=params, headers=headers).json()
    if response['success'] is True:
        return True
    else:
        return False


def confirm_code(phone_number, country_code, verification_code):

    """
    Confirm Verification Code entered by the user
    :param phone_number:
    :param country_code:
    :param verification_code:
    :return: Boolean
    """
    params = {
        'verification_code': verification_code,
        'phone_number': phone_number,
        'country_code': country_code
    }

    response = requests.get(verify_url, params=params, headers=headers).json()
    if response['success'] is True:
        return True
    else:
        return False




