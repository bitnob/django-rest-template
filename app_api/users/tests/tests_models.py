from json import loads
from django.test import TestCase
from app_api.users.models import User

from rest_framework.test import APITestCase
from rest_framework import status


class UserAPITestCase(APITestCase):
    """This test case offers user fixtures and user methods"""

    user1 = {'username':'test-user-1', 'password':'test-pass'}
    user2 = {'username':'test-user-2', 'password':'test-pass'}

    def get_user(self, cred):
        return User.objects.get(username=cred['username'])

    def register(self, cred):
        response = self.client.post('/register/', cred)
        return response

    def get_token(self, cred):
        data = {'grant_type':'password', 'username': cred['username'],\
        'password':cred['password'], 'client_id': cred['username']}

        response = self.client.post('/oauth2/access_token', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = loads(response.content)

        self.assertTrue('access_token' in response_data)
        token = response_data['access_token']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)


class RegistrationTest(UserAPITestCase):
    """Testing the registration of new users and login"""

    def test_register(self):
        """ Register a user acccount. """

        response = self.register(self.user1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    def test_token(self):
        """ Register, get token """

        self.register(self.user1)
        self.get_token(self.user1)

    def test_register_login(self):
        """ Register and login with a user account. """

        self.register(self.user1)
        self.get_token(self.user1)

        response = self.client.get('/todos/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
