from __future__ import unicode_literals

import logging

from api.exceptions import (
  BadPickException,
  DuplicateMemberException,
  InvalidMemberException,
  TooFewMembersException,
  TooManyMembersException,
)
from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from random import shuffle
from rest_framework.authtoken.models import Token

logger = logging.getLogger('nba-logger')

SUPPORTED_POOL_SIZES = (2, 3, 5, 6)


# This code is triggered whenever a new user has been created and saved to the database
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
  if created:
    Token.objects.create(user=instance)


class Pool(models.Model):
  """
  `Pool` has many `User`s through `Membership`. User is part of many `Pool`s
  through the `Membership`.
  """
  name = models.CharField(max_length=128)
  max_size = models.PositiveSmallIntegerField(default=5)
  members = models.ManyToManyField(User, through='Membership')

  def add_member(self, user):
    """
    Adds a new member to the Pool. If, after adding the new member, we're at
    `self.max_size`, then kicks off the Pool.
    """
    # 0. Verify that we can add another unique member.
    original_pool_size = len(self.members.all())
    if original_pool_size >= self.max_size:
      raise TooManyMembersException("Cannot add any more members to the Pool.")

    if user in self.members.all():
      raise DuplicateMemberException("Cannot add the same member to the Pool twice.")

    # 1. Add the new member to the Pool.
    curr_time = datetime.now()
    Membership.objects.create(pool=self, user=user, date_joined=curr_time)

    # 2. If we now have enough members in the pool to begin, compute the
    # draft order and draft status.
    new_members = self.members.all()
    assert len(new_members) == original_pool_size + 1
    if len(new_members) == self.max_size:
      self.begin_draft()

    return self

  def remove_member(self, user):
    """
    Removes the user from the membership list of the Pool
    """
    if user not in self.members.all():
      raise InvalidMemberException("Cannot remove a member that isn't part of the pool")

    m = Membership.objects.get(user=user, pool=self)
    m.delete()

  @staticmethod
  def compute_draft_order(user_ids):
    """
    Given a list of `user_ids`, randomly shuffles the `user_ids` and returns
    them in a draft order.

    Args:
      user_ids(iterable): A list of `user_ids` of the members of the pool.

    Returns:
      user_ids_by_draft_order(dict): Map from draft_order -> user_id.
        E.g. {pick_1-> user_1234}

    Raises:
      AssertionError: If `user_ids` is the incorrect length.
    """
    # 0. De-dupe the user_ids and sanity check.
    pool_size = len(set(user_ids))
    assert pool_size in SUPPORTED_POOL_SIZES

    # 1. Shuffle the user_ids randomly.
    random_user_ids = list(set(user_ids))
    shuffle(random_user_ids)

    logger.info('random user_ids: %s' % random_user_ids)

    # 2. Map from size of pool to the order.
    draft_order_by_pool_size = {
      2: [1, 2, 2, 1, 2, 1, 2, 1, 1, 2, 2, 1, 1, 2, 2, 1, 1, 2, 2, 1, 1, 2, 2, 1, 1, 2, 2, 1, 2, 1],
      3: [1, 2, 3, 3, 2, 1, 2, 1, 3, 3, 2, 1, 1, 2, 3, 3, 2, 1, 1, 2, 3, 3, 2, 1, 2, 1, 3, 3, 2, 1],
      5: [1, 2, 3, 4, 5, 5, 4, 3, 2, 1, 1, 2, 3, 5, 4, 5, 4, 3, 2, 1, 4, 2, 3, 1, 5, 5, 4, 3, 2, 1],
      6: [1, 2, 3, 4, 5, 6, 6, 5, 4, 3, 2, 1, 5, 2, 4, 3, 6, 1, 5, 6, 4, 2, 3, 1, 6, 5, 4, 3, 2, 1],
    }

    # 3. Grab the relevant draft order and populate the dict.
    draft_order = draft_order_by_pool_size[pool_size]
    logger.info('draft order: %s' % draft_order)
    user_ids_by_draft_order = {}
    for pick_index, user_index in enumerate(draft_order):
      user_ids_by_draft_order[pick_index + 1] = random_user_ids[user_index - 1]

    logger.info('user_ids_by_draft_order: %s' % user_ids_by_draft_order)

    return user_ids_by_draft_order

  def begin_draft(self):
    """
    Verifies that we have enough members to start the pool and then creates
    empty DraftPicks for each member of the Pool.

    Returns:
      Nothing but creates a series of DraftPicks for each member.

    Raises:
      AssertionError: If we cannot begin the draft yet.
    """
    members = self.members.all()
    if len(members) != self.max_size:
      raise TooFewMembersException("Not enough members to start the pool!")

    users_by_id = {member.id: member for member in members}
    user_ids_by_draft_order = Pool.compute_draft_order(users_by_id.keys())

    logger.info('user_ids_by_draft_order: %s' % user_ids_by_draft_order)
    for (pick, user_id) in user_ids_by_draft_order.iteritems():
      user = users_by_id[user_id]
      DraftPick.objects.create(pool=self, user=user, draft_pick_number=pick)

  def make_draft_pick(self, user, team):
    # 0. Ensure that only the next user up can make a pick.
    pick = DraftPick.objects.filter(pool=self, team=None).order_by('draft_pick_number')[0]
    if pick.user != user:
      raise BadPickException("Not user: %s's turn to pick!" % user.username)

    # 1. Ensure that the user doesn't try to pick a team that has already been
    # chosen.
    dps = DraftPick.objects.filter(pool=self).exclude(team__isnull=True).order_by('draft_pick_number')
    teams_picked = [dp.team for dp in dps]
    if team in teams_picked:
      raise BadPickException("Can't pick a team %s that has already been chosen" % team.team_full_name)

    pick.team = team
    pick.save()

    return self

  def __unicode__(self):
    return '<Pool (name=%s, max_size=%s)>' % (self.name, self.max_size)


class Membership(models.Model):
  """
  `Membership` defines the relation between `User` and `Pool`.
  A `User` joins a `Pool` through their membership.
  """
  pool = models.ForeignKey(Pool, on_delete=models.CASCADE)
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  date_joined = models.DateField()


class Team(models.Model):
  """
  Autopopulated from `nba_teams.yaml`.
  """
  league_short_code = models.CharField(max_length=256)
  league_full_name = models.CharField(max_length=256)

  team_short_code = models.CharField(max_length=256)
  team_full_name = models.CharField(max_length=256)

  def __unicode__(self):
    return '<Team %s:%s>' % (self.league_short_code, self.team_full_name)


class DraftPick(models.Model):
  pool = models.ForeignKey(Pool, on_delete=models.CASCADE)
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  team = models.ForeignKey(Team, on_delete=models.CASCADE, blank=True, null=True)
  draft_pick_number = models.IntegerField(default=1)
