from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models

from django.conf import settings
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

# A Pool has many Users through Membership
# A User is part of many Pools
# class Pool(models.Model):
#   name = models.CharField(max_length=128)
#   members = models.ManyToManyField(
#     User,
#     through='Membership',
#     through_fields=('pool', 'user'),
#   )

# class Membership(models.Model):
#   pool = models.ForeignKey(Pool, on_delete=models.CASCADE)
#   user = models.ForeignKey(User, on_delete=models.CASCADE)
#   inviter = models.ForeignKey(
#     User,
#     on_delete=models.CASCADE,
#     related_name="membership_invites",
#   )
#   invite_reason = models.CharField(max_length=256)
#   join_date = models.DateField()

# class Team(models.Model):
#   name = models.CharField(max_length=50)
#   short_name = models.CharField(max_length=50)

# class Draft(models.Model):
#   user = models.ForeignKey(User, on_delete=models.CASCADE)
#   team = models.ForeignKey(Team, on_delete=models.CASCADE)
#   draft_pick_number = models.IntegerField()
