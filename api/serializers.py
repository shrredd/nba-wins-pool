import logging
import time

from api.models import (
  DraftPick,
  Membership,
  Pool,
  SUPPORTED_POOL_SIZES,
  Team,
)
from django.contrib.auth.models import User
from rest_framework import serializers

logger = logging.getLogger('nba-logger')


######################################################################
# USER SERIALIZER
######################################################################
class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ('id', 'username', 'email', 'password')
    read_only_fields = (
      'is_staff', 'is_superuser', 'is_active', 'date_joined',
    )
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

    # A coresponding authentication token for this user is created in models.py
    # t = Token.objects.create(user=user)
    return user

  @staticmethod
  def to_data(user):
    assert isinstance(user, User)

    return {
      'id': user.id,
      'username': user.username,
      'email': user.email,
    }

  @staticmethod
  def to_data_batch(users):
    """ `users` can be any iterable value, e.g. a QuerySet instead of just a list """
    return [UserSerializer.to_data(user) for user in users]


######################################################################
# MEMBERSHIP SERIALIZER
######################################################################
class MembershipSerializer(serializers.HyperlinkedModelSerializer):
  class Meta:
    model = Membership
    fields = ('user', 'date_joined')


######################################################################
# TEAM SERIALIZER
######################################################################
class TeamSerializer(object):
  @staticmethod
  def to_data(team):
    assert isinstance(team, Team)
    return {
      'league_short_code': team.league_short_code,
      'league_full_name': team.league_full_name,
      'team_id': team.team_short_code,
      'team_full_name': team.team_full_name,
    }

  @staticmethod
  def to_data_batch(teams):
    return [TeamSerializer.to_data(team) for team in teams]


######################################################################
# DRAFT PICK SERIALIZER
######################################################################
class DraftPickSerializer(object):
  @staticmethod
  def to_data(draft_pick):
    assert isinstance(draft_pick, DraftPick)
    return {
      'user': UserSerializer.to_data(draft_pick.user),
      'team': TeamSerializer.to_data(draft_pick.team) if draft_pick.team is not None else None,
      'draft_pick_number': draft_pick.draft_pick_number,
    }

  @staticmethod
  def to_data_batch(draft_picks):
    return [DraftPickSerializer.to_data(draft_pick) for draft_pick in draft_picks]


######################################################################
# POOL SERIALIZER
######################################################################
class PoolSerializer(object):
  @staticmethod
  def to_data(pool):
    logger.info('pool.draft_pick_set: %s' % pool.draftpick_set.all())
    return {
      'id': pool.id,
      'name': pool.name,
      'max_size': pool.max_size,
      'members': UserSerializer.to_data_batch(pool.members.all()),
      'draft_status': DraftPickSerializer.to_data_batch(pool.draftpick_set.all()),
    }

  @staticmethod
  def to_data_batch(pools):
    # TODO(shravan): This should be defined the inverse way. `to_data` should
    # be defined in terms of `to_data_batch`.
    return [PoolSerializer.to_data(pool) for pool in pools]

  @staticmethod
  def create_from_data(pool_data):
    # 0. Validate the `pool_data`
    assert 'name' in pool_data and isinstance(pool_data['name'], basestring)
    assert 'max_size' in pool_data

    pool_name = pool_data['name']
    member_usernames = pool_data['members']
    max_size = int(pool_data['max_size'])
    assert max_size in SUPPORTED_POOL_SIZES

    # 1. Verify that the usernames passed in correspond to actual users.
    users = None
    if len(member_usernames) > 0:
      users = User.objects.filter(username__in=member_usernames)
      if len(users) != len(set(member_usernames)):
        raise Exception('Bad usernames passed in...')

    # 2. Create the Pool.
    pool = Pool.objects.create(name=pool_name, max_size=max_size)

    # 3. Add each user as a new member.
    for user in users:
      pool.add_member(user)

    return pool


class PoolMemberSerializer(object):
  @staticmethod
  def update_from_data(pool_id, pool_member_data):
    """
    Adds a new member whose username is in `pool_data`.

    Args:
      pool_id: The pool id of an existing pool
      pool_data: Expected to be in the format:
        {"username": <username of new member>}

    Raises:
      User.DoesNotExist: If the user within `pool_data` doesn't exist.
      Pool.DoesNotExist: If the pool doesn't exist.
      TooManyMembersException: If we attempt to add more users than the pool
        can handle.
    """
    # 0. Validate the `pool_data` and `pool_id`.
    assert pool_id.isdigit()
    assert "username" in pool_member_data
    member_username = pool_member_data["username"]
    pool_id = long(pool_id)

    # 1. Validate that a user exists with `member_username`
    user = User.objects.get(username=member_username)
    if not user:
      raise User.DoesNotExist()

    # 2. Attempt to fetch the Pool.
    pool = Pool.objects.get(id=pool_id)
    if not pool:
      raise Pool.DoesNotExist()

    logger.info('pool: %s' % pool)
    # 3. Add the new member to the pool.
    pool.add_member(user)

    logger.info('pool after adding member: %s' % pool.members.all())

    return pool.members.all()

  @staticmethod
  def to_data(pool_member):
    return UserSerializer.to_data(pool_member)

  @staticmethod
  def to_data_batch(pool_members):
    return UserSerializer.to_data_batch(pool_members)
