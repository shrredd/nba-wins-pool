from __future__ import unicode_literals

from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from api import shravan


# This code is triggered whenever a new user has been created and saved to the database
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
  shravan.SAY('create auth token called...')
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

  def __unicode__(self):
    return '<Pool (name=%s)>' % (self.name)


class Membership(models.Model):
  """
  `Membership` defines the relation between `User`
  """
  pool = models.ForeignKey(Pool, on_delete=models.CASCADE)
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  date_joined = models.DateField()

# class Team(models.Model):
#   name = models.CharField(max_length=50)
#   short_name = models.CharField(max_length=50)

# class Draft(models.Model):
#   user = models.ForeignKey(User, on_delete=models.CASCADE)
#   team = models.ForeignKey(Team, on_delete=models.CASCADE)
#   draft_pick_number = models.IntegerField()


def create_pool(pool_name, usernames=None):
  """
  Args:
    pool_name (unicode): The human readable name of the pool to be created.
    usernames (list): An iterable of the users who are to be initially added to
      this pool.
  """
  from api.models import Pool
  if not pool_name:
    raise ValueError("No pool_name passed in")

  # 1. Create the Pool
  p = Pool.objects.create(name=pool_name)

  # 2. Optionally create the members of the pool and add them
  if usernames is not None and len(usernames) > 0:
    users = User.objects.filter(username__in=usernames)
    if len(users) != len(set(usernames)):
      raise ValueError("Username passed in doesnt exist")

    # TODO(shravan): Investigate a way to create memberships all at once instead
    # of looping here
    for u in users:
      m = Membership.objects.create(pool=p, user=u, date_joined=datetime.now())

  return p
