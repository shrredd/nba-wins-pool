from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

import logging
logger = logging.getLogger('nba-logger')


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
