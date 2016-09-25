from api.models import (Membership, Pool)
from django.contrib.auth.models import User
from datetime import datetime
from rest_framework import serializers
from rest_framework.authtoken.models import Token

import logging
logger = logging.getLogger('testlogger')


class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ('id', 'username', 'email', 'password')
    read_only_fields = ('is_staff', 'is_superuser',
                        'is_active', 'date_joined',)
    extra_kwargs = {
      'password': {'write_only': True},
      'id': {'read_only': True},
      'url': {'lookup_field': 'username'}
    }

  def create(self, validated_data):
    # Create a new User and save to the DB.
    user = User(
      email=validated_data['email'],
      username=validated_data['username'],
    )
    user.set_password(validated_data['password'])
    user.save()

    # Create a coresponding authentication token for this user
    # t = Token.objects.create(user=user)

    return user


class MembershipSerializer(serializers.HyperlinkedModelSerializer):
  class Meta:
    model = Membership
    fields = ('user', 'date_joined')


# class PoolSerializer(serializers.HyperlinkedModelSerializer):
#   members = serializers.HyperlinkedRelatedField(
#     many=True,
#     read_only=True,
#     view_name='membership-detail',
#     lookup_field='username'
#   )

#   class Meta:
#     model = Pool
#     fields = ('id', 'name', 'members')
#     read_only_fields = ('id', )
#     validators = []

#   def validate(self, data):
#     logger.info('validate called: %s' % data)
#     return data

#   def create(self, validated_data):

import json
import time


class PoolSerializer(object):
  @staticmethod
  def to_data(pool):
    members_list = [{
      'username': user.username,
      'email': user.email,
      'date_joined': time.mktime(user.date_joined.timetuple())
    } for user in pool.members.all()]

    return {
      'name': pool.name,
      'max_size': pool.max_size,
      'members': members_list
    }

  @staticmethod
  def to_data_batch(pools):
    # TODO(shravan): This should be defined the inverse way. `to_data` should
    # be defined in terms of `to_data_batch`.
    return [PoolSerializer.to_data(pool) for pool in pools]

  @staticmethod
  def from_data(pool_data):
    # 0. Validate the `pool_data`
    assert 'name' in pool_data and isinstance(pool_data['name'], basestring)
    assert 'max_size' in pool_data

    logger.info('within from_data: %s' % pool_data)
    pool_name = pool_data['name']
    max_size = int(pool_data['max_size'])
    assert max_size in (2, 3, 5, 6)
    member_usernames = pool_data['members']

    # 1. Verify that the usernames passed in correspond to actual users.
    users = None
    if len(member_usernames) > 0:
      users = User.objects.filter(username__in=member_usernames)
      logger.info('len(users): %s' % len(users))
      logger.info('len(member names): %s' % len(set(member_usernames)))
      if len(users) != len(set(member_usernames)):
        raise Exception('Bad usernames passed in...')

    # 2. Create the Pool.
    pool = Pool.objects.create(
      name=pool_name,
      max_size=max_size
    )

    # 3. Create the Membership for each of the Users.
    if users is not None:
      curr_time = datetime.now()
      for u in users:
        Membership.objects.create(pool=pool, user=u, date_joined=curr_time)

    return pool
