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
    t = Token.objects.create(user=user)

    return user

# class MembersByPoolList(generics.ListAPIView):
#   model = User
#   serializer_class = UserSerializer

#   def get_queryset(self):
#     user_pk = self.kwargs.get('user_pk', None)
#     if user_pk is not None:
#         return .objects.filter(user=user_pk)
#     return []


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
      'members': members_list
    }

  @staticmethod
  def to_data_batch(pools):
    # TODO(shravan): This should be defined the inverse way. `to_data` should
    # be defined in terms of `to_data_batch`.
    return [PoolSerializer.to_data(pool) for pool in pools]

  @staticmethod
  def from_data(pool_data):
    assert 'name' in pool_data

    logger.info('pool_data: %s' % pool_data)
    member_usernames = pool_data.get('members', [])
    logger.info('member usernames: %s' % member_usernames)

    join_time = datetime.now()
    pool = Pool.objects.create(name=pool_data['name'])

    if len(member_usernames) > 0:
      users = User.objects.filter(username__in=member_usernames)
      if len(users) != len(member_usernames):
        raise Exception('Bad usernames passed in...')

      for u in users:
        m = Membership.objects.create(pool=p, user=u, date_joined=join_time)

    logger.info('*****************************')
    logger.info('pool: %s' % pool)
    logger.info('pool name: %s' % pool.name)
    logger.info('pool members: %s' % pool.members)
    logger.info('*****************************')
    return pool
