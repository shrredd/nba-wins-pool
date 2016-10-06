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
    r_dict = json.loads(r.content)
    assert isinstance(r_dict['token'], unicode)
    return r_dict['token']

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


class PoolTests(unittest.TestCase):
  """ Note: The below are raw examples of using the API to create, get, update
  and delete pools """
  def create_pool(self):
    >>> r = requests.post("http://localhost:3000/api/v1/pools/", json={'name': 'Shreya Pool', 'members': ['shravan'], 'max_size': 2}, headers={'Authorization': 'Token 8dc44a0fb3e656c7818f270710b6fe33a37c017a'})
    2016-10-06 22:22:41,478 - requests.packages.urllib3.connectionpool - INFO - Starting new HTTP connection (1): localhost
    2016-10-06 22:22:41,509 - requests.packages.urllib3.connectionpool - DEBUG - "POST /api/v1/pools/ HTTP/1.1" 201 None
    >>> r.content
    '{"members":[{"username":"shravan","id":1,"email":"shravan.g.reddy@gmail.com"}],"draft_status":[],"id":35,"max_size":2,"name":"Shreya Pool"}'

  def get_pool(self):
    >>> r = requests.get("http://localhost:3000/api/v1/pools/42", headers={'Authorization': 'Token 8dc44a0fb3e656c7818f270710b6fe33a37c017a'})
    2016-10-06 23:30:18,889 - requests.packages.urllib3.connectionpool - INFO - Starting new HTTP connection (1): localhost
    2016-10-06 23:30:18,908 - requests.packages.urllib3.connectionpool - DEBUG - "GET /api/v1/pools/42 HTTP/1.1" 200 None
    >>> r.content
    '{"members":[{"username":"seconduser","id":2,"email":"seconduser@gmail.com"},{"username":"shravan","id":1,"email":"shravan.g.reddy@gmail.com"}],"draft_status":[{"draft_pick_number":1,"user":{"username":"shravan","id":1,"email":"shravan.g.reddy@gmail.com"},"team":null},{"draft_pick_number":2,"user":{"username":"seconduser","id":2,"email":"seconduser@gmail.com"},"team":null}],"id":42,"max_size":2,"name":"Shreya Pool"}'


class PoolMembersTests(unittest.TestCase):

  def add_member_to_pool(self):
    >>> r = requests.put("http://localhost:3000/api/v1/pools/42/members/", json={'username': 'seconduser'}, headers={'Authorization': 'Token 8dc44a0fb3e656c7818f270710b6fe33a37c017a'})
    2016-10-06 23:29:00,994 - requests.packages.urllib3.connectionpool - INFO - Starting new HTTP connection (1): localhost
    2016-10-06 23:29:01,027 - requests.packages.urllib3.connectionpool - DEBUG - "PUT /api/v1/pools/42/members/ HTTP/1.1" 200 None
    >>> r.content
    '[{"username":"seconduser","id":2,"email":"seconduser@gmail.com"},{"username":"shravan","id":1,"email":"shravan.g.reddy@gmail.com"}]'

  def remove_member_from_pool(self):
    >>> r = requests.delete("http://localhost:3000/api/v1/pools/42/members/", headers={'Authorization': 'Token 8dc44a0fb3e656c7818f270710b6fe33a37c017a'})
    2016-10-06 23:49:53,434 - requests.packages.urllib3.connectionpool - INFO - Starting new HTTP connection (1): localhost
    2016-10-06 23:49:53,527 - requests.packages.urllib3.connectionpool - DEBUG - "DELETE /api/v1/pools/42/members/ HTTP/1.1" 204 0
    >>> r.content
    ''


class PoolDraftTests(unittest.TestCase):
  def get_draft_picks(self):
    >>> r = requests.get("http://localhost:3000/api/v1/pools/42/draft/", headers={'Authorization': 'Token 8dc44a0fb3e656c7818f270710b6fe33a37c017a'})
    2016-10-06 23:56:16,523 - requests.packages.urllib3.connectionpool - INFO - Starting new HTTP connection (1): localhost
    2016-10-06 23:56:16,543 - requests.packages.urllib3.connectionpool - DEBUG - "GET /api/v1/pools/42/draft/ HTTP/1.1" 200 None
    >>> r.content
    '[{"draft_pick_number":1,"user":{"username":"shravan","id":1,"email":"shravan.g.reddy@gmail.com"},"team":null},{"draft_pick_number":2,"user":{"username":"seconduser","id":2,"email":"seconduser@gmail.com"},"team":null}]'

  def make_draft_pick(self):
    >>> r = requests.put("http://localhost:3000/api/v1/pools/42/draft/", json={'team_id': 'houston-rockets'}, headers={'Authorization': 'Token 8dc44a0fb3e656c7818f270710b6fe33a37c017a'})
    2016-10-07 00:44:27,059 - requests.packages.urllib3.connectionpool - INFO - Starting new HTTP connection (1): localhost
    2016-10-07 00:44:27,092 - requests.packages.urllib3.connectionpool - DEBUG - "PUT /api/v1/pools/42/draft/ HTTP/1.1" 200 None
    >>> r.content
    '[{"draft_pick_number":2,"user":{"username":"seconduser","id":2,"email":"seconduser@gmail.com"},"team":{"league_full_name":"National Basketball Association","team_id":"utah-jazz","team_full_name":"Utah Jazz","league_short_code":"NBA"}},{"draft_pick_number":1,"user":{"username":"shravan","id":1,"email":"shravan.g.reddy@gmail.com"},"team":{"league_full_name":"National Basketball Association","team_id":"houston-rockets","team_full_name":"Houston Rockets","league_short_code":"NBA"}}]'
