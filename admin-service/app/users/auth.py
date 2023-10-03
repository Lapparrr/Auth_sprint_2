import http
import json

import requests
from django.conf import settings
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from users.backoff import backoff

User = get_user_model()

@backoff()
def send_data(url, data):

    response = requests.post(url, data=data)
    data = response.json()
    return data


class CustomBackend(BaseBackend):

    @backoff
    def authenticate(self, request, username=None, password=None):
        url = settings.AUTH_API_LOGIN_URL
        payload = {'email': username, 'password': password}
        data = send_data(url, data=json.dumps(payload))
        user, created = User.objects.get_or_create(id=data['id'], )
        user.email = data.get('email')
        user.first_name = data.get('first_name')
        user.last_name = data.get('last_name')
        user.is_admin = False
        for values in data.get('roles'):
            if values['name'] == 'admin':
                user.is_admin = True
        user.is_active = True
        user.save()
        return user

    @backoff
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
