import logging

from api.models import Pool, Membership
from api.permissions import IsStaffOrTargetUser
from api.serializers import (
  PoolSerializer,
  UserSerializer,
  TooManyMembersException,
)

from django.contrib.auth.models import User
from django.http import Http404

from rest_framework import (status, viewsets)
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

# Set up logger
logger = logging.getLogger('nba-logger')


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
# POOL RELATED FUNCTIONS
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


class PoolDetail(APIView):
  """ Retrieve, update or delete a pool instance. """
  def get_object(self, pool_id):
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
    pool = self.get_object(pool_id)
    logger.info('request data: %s' % request.data)
    try:
      pool = PoolSerializer.update_from_data(pool_id, request.data)
      return Response(PoolSerializer.to_data(pool))
    except (User.DoesNotExist, Pool.DoesNotExist, TooManyMembersException):
      return Response('Bad Request', status=status.HTTP_400_BAD_REQUEST)

  def delete(self, request, pool_id, format=None):
    """
    Deletes the pool at `pk`.
    """
    pool = self.get_object(pk)
    pool.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


class PoolsByUser(APIView):
  """
  Allows fetching a particular user's pools.
  """
  def get(self, request, username, format=None):
    user = User.objects.filter(username=username)
    memberships = Membership.objects.filter(user=user)
    pools = [membership.pool for membership in memberships]

    if pools:
      pool_data = PoolSerializer.to_data_batch(pools)
      return Response(pool_data, status=status.HTTP_201_CREATED)

    return Response("Bad request", status=status.HTTP_400_BAD_REQUEST)

  def get_permissions(self):
    # Allow non-authenticated user to create via POST
    return (AllowAny() if self.request.method == 'POST' else IsStaffOrTargetUser()),
