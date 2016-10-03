import json
import requests
import unittest

from api.models import create_pool
from django.test import TestCase

# Create your tests here.

DOMAIN = 'http://localhost:8000'


class UserTests(unittest.TestCase):

  def _create_user(self, username=None, first_name=None, last_name=None):
    r = requests.post(
      "%s/api/v1/accounts/" % DOMAIN,
      json={
        "username": username if username is not None else "shravan",
        "password": "pass",
        "first_name": first_name if first_name is not None else "Shravan",
        "last_name": last_name if last_name is not None else "Reddy"
      }
    )

    # 1. Assert the response is as expected.
    assert r.status_code == 201

    # 2. Verify the structure of the response.
    r_dict = json.loads(r.content)
    assert 'id' in r_dict and isinstance(r_dict['id'], int)
    assert 'username' in r_dict and isinstance(r_dict['username'], unicode)
    assert 'email' in r_dict and isinstance(r_dict['email'], unicode)

    return r_dict

  def _fetch_auth_token(self, username=None):
    r = requests.post(
      "%s/api/v1/auth/" % DOMAIN,
      json={
        'username': 'shravan',
        'password': 'password'
      }
    )

    assert r.status_code == 200
    token = json.loads(r.content)
    assert isinstance(token, unicode)
    return token

  def _fetch_user(self, token, username=None):
    r = requests.get(
      "%s/api/v1/accounts/%s" % (DOMAIN, username if username is not None else 'shravan'),
      headers={'Authorization': 'Token %s' % token}
    )

    assert r.status_code == 200
    r_dict = json.loads(r.content)
    assert 'id' in r_dict and isinstance(r_dict['id'], int)
    assert 'username' in r_dict and isinstance(r_dict['username'], unicode)
    assert 'email' in r_dict and isinstance(r_dict['email'], unicode)

    return r_dict

  def test_create_user(self):
    self._create_user()

  def test_auth_user(self):
    self._create_user()
    self._fetch_auth_token()

  def test_fetch_user(self):
    self._create_user()
    token = self._fetch_auth_token()
    self._fetch_user(token=token)
