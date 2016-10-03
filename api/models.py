from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from random import shuffle
from rest_framework.authtoken.models import Token

import logging
logger = logging.getLogger('nba-logger')

SUPPORTED_POOL_SIZES = (2, 3, 5, 6)


# This code is triggered whenever a new user has been created and saved to the database
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
  if created:
    Token.objects.create(user=instance)


# A User is part of many Pools
class Pool(models.Model):
  """
  `Pool` has many `User`s through `Membership`. User is part of many `Pool`s
  through the `Membership`.
  """
  name = models.CharField(max_length=128)
  members = models.ManyToManyField(User, through='Membership')
  max_size = models.PositiveSmallIntegerField(default=5)

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
    random_user_ids = shuffle(list(set(user_ids)))

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
    user_ids_by_draft_order = {}
    for pick in draft_order:
      user_ids_by_draft_order[pick] = random_user_ids[pick - 1]

    logger.info('user_ids_by_draft_order: %s' % user_ids_by_draft_order)

    return user_ids_by_draft_order

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
  team = models.ForeignKey(Team, on_delete=models.CASCADE)
  draft_pick_number = models.IntegerField(default=1)
