import logging

from api.exceptions import TooManyMembersException
from api.models import Membership, Pool, Team
from api.permissions import IsStaffOrTargetUser
from api.serializers import (
  DraftPickSerializer,
  PoolSerializer,
  PoolMemberSerializer,
  UserSerializer,
)

from django.contrib.auth.models import User
from django.http import Http404

from rest_framework import (status, viewsets)
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

# Set up logger
logger = logging.getLogger('nba-logger')


######################################################################
# USER DETAILS
######################################################################
class UserViewSet(viewsets.ModelViewSet):
  """
  ViewSet for generic django User.
  """
  serializer_class = UserSerializer
  model = User
  queryset = User.objects.all().order_by('-date_joined')
  lookup_field = ('username')
  parser_classes = (JSONParser, )

  def get_permissions(self):
    # Allow non-authenticated user to create via POST
    return (AllowAny() if self.request.method == 'POST' else IsStaffOrTargetUser()),


# class MembershipViewSet(viewsets.ModelViewSet):
#   serializer_class = MembershipSerializer
#   model = Membership
#   queryset = Membership.objects.all()

######################################################################
# LIST OF ALL POOLS
######################################################################
class PoolList(APIView):
  parser_classes = (JSONParser,)

  """ List all pools, or create a new pool. """
  def get(self, request, format=None):
    pools = Pool.objects.all()
    logger.info('type of pools: %s' % type(pools[0]))
    serialized_data = PoolSerializer.to_data_batch(pools)

    return Response(serialized_data)

  def post(self, request, format=None):
    logger.info('original pool data: %s' % request.data)
    pool = PoolSerializer.create_from_data(request.data)
    # if serializer.is_valid():
    #     serializer.save()
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)
    if pool:
      pool_data = PoolSerializer.to_data(pool)
      return Response(pool_data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


######################################################################
# DETAILS OF A SPECIFIC POOL
######################################################################
class PoolDetail(APIView):
  """ Retrieve, update or delete a pool instance. """
  def get_object(self, pool_id):
    try:
      return Pool.objects.get(id=pool_id)
    except Pool.DoesNotExist:
      raise Http404

  def get(self, request, pool_id):
    """Fetch the draft picks for a particular pool"""
    pool = self.get_object(pool_id)
    pool_data = PoolSerializer.to_data(pool)
    return Response(pool_data)

  def delete(self, request, pool_id, format=None):
    """ Deletes the Pool entirely """
    pass


class PoolMembers(APIView):

  def _get_object(self, pool_id):
    try:
      return Pool.objects.get(id=pool_id)
    except Pool.DoesNotExist:
      raise Http404

  def put(self, request, pool_id, format=None):
    """
    Allows a new user to join an existing `pool_id`.

    Args:
      `request.data` is expected to be in the format:
      {
        "member": <username of new member>
      }
      If the pool already has reached `max_size`, this will raise a 400.
    """
    logger.info('request data: %s' % request.data)
    try:
      pool_members = PoolMemberSerializer.update_from_data(pool_id, request.data)
      return Response(PoolMemberSerializer.to_data_batch(pool_members))
    except (User.DoesNotExist, Pool.DoesNotExist, TooManyMembersException):
      return Response('Bad Request', status=status.HTTP_400_BAD_REQUEST)

  def delete(self, request, pool_id, format=None):
    """
    Removes the logged in user from the pool specified by pool_id.
    """
    pool = self._get_object(pool_id)
    user = request.user
    pool.remove_member(user)
    return Response(status=status.HTTP_204_NO_CONTENT)


######################################################################
# DETAILS OF THE DRAFT CORRESPONDING TO THE POOL
######################################################################
class DraftDetail(APIView):
  """
  Retrieve the details of the draft corresponding to a particular pool.
  """
  def get_pool(self, pool_id):
    try:
      return Pool.objects.get(id=pool_id)
    except Pool.DoesNotExist:
      raise Http404

  def get_draft(self, pool_id):
    pool = self.get_pool(pool_id)
    draft_picks = pool.draftpick_set.all()

    if draft_picks == [] or draft_picks is None:
      raise Http404

    return draft_picks

  def get(self, request, pool_id):
    """Fetch the draft picks for a particular pool"""
    draft_picks = self.get_draft(pool_id)
    draft_pick_data = DraftPickSerializer.to_data_batch(draft_picks)
    return Response(draft_pick_data)

  def put(self, request, pool_id, format=None):
    pool = self.get_pool(pool_id)
    user = request.user

    team_short_code = request.data['team_id']
    team = Team.objects.get(team_short_code=team_short_code)

    pool = pool.make_draft_pick(user, team)
    draft_picks = self.get_draft(pool.id)
    draft_pick_data = DraftPickSerializer.to_data_batch(draft_picks)
    return Response(draft_pick_data)


######################################################################
# POOLS FOR A SPECIFIC USER
######################################################################
class PoolsByUser(APIView):
  permission_classes = (IsAuthenticated,)

  """
  Allows fetching a particular user's pools.
  """
  def get(self, request, username, format=None):
    user = User.objects.filter(username=username)
    memberships = Membership.objects.filter(user=user)
    pools = [membership.pool for membership in memberships]

    logger.info('membership pools: %s type(%s)' % (pools, type(memberships[0].pool)))

    if pools:
      pool_data = PoolSerializer.to_data_batch(pools)
      return Response(pool_data, status=status.HTTP_201_CREATED)

    return Response("Bad request", status=status.HTTP_400_BAD_REQUEST)

  # def get_permissions(self):
    # Allow non-authenticated user to create via POST
    # return (AllowAny() if self.request.method == 'POST' else IsStaffOrTargetUser()),
