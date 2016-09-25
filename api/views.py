import logging

from api.permissions import IsStaffOrTargetUser
from api.models import Pool, Membership
from api.serializers import (PoolSerializer, UserSerializer, MembershipSerializer)

from django.contrib.auth.models import User
from django.http import Http404

from rest_framework import (status, viewsets)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

# Set up logger
logger = logging.getLogger('testlogger')


class UserViewSet(viewsets.ModelViewSet):
  """
  ViewSet for generic django User.
  """
  serializer_class = UserSerializer
  model = User
  queryset = User.objects.all().order_by('-date_joined')
  lookup_field = ('username')

  def get_permissions(self):
    # Allow non-authenticated user to create via POST
    return (AllowAny() if self.request.method == 'POST' else IsStaffOrTargetUser()),


# class MembershipViewSet(viewsets.ModelViewSet):
#   serializer_class = MembershipSerializer
#   model = Membership
#   queryset = Membership.objects.all()

########################################################
# Pool Related Functions
########################################################
def create_pool(pool_nam, usernames=None):
  logger.info('create called with validated_data: %s' % validated_data)
  # 1. Create the Pool
  p = Pool.objects.create(name=pool_name)

  # 2. Create the membership if member usernames are passed in.
  if 'members' in validated_data and len(validated_data['members']) > 0:
    member_usernames = validated_data['members']
    members = User.objects.filter(username__in=member_usernames)

    for u in users:
      date_joined = datetime.now()
      m = Membership.objects.create(pool=p, user=m, date_joined=date_joined)

  return p


class PoolList(APIView):
  """ List all pools, or create a new pool. """
  def get(self, request, format=None):
    pools = Pool.objects.all()
    logger.info('type of pools: %s' % type(pools[0]))
    serialized_data = PoolSerializer.to_data_batch(pools)

    return Response(serialized_data)

  def post(self, request, format=None):
    logger.info('original pool data: %s' % request.data)
    pools = PoolSerializer.from_data(request.data)
    # if serializer.is_valid():
    #     serializer.save()
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)
    if pools:
      return Response(request.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PoolDetail(APIView):
  """ Retrieve, update or delete a pool instance. """
  def get_object(self, pk):
    try:
      return Pool.objects.get(pk=pk)
    except Pool.DoesNotExist:
      raise Http404

  def get(self, request, pk, format=None):
    pool = self.get_object(pk)
    serializer = PoolSerializer(pool, context={'request': request})
    return Response(serializer.data)

  def put(self, request, pk, format=None):
    """
    Updates an existing Pool with the information passed in through
    request.
    """
    pool = self.get_object(pk)
    serializer = PoolSerializer(pool, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  def delete(self, request, pk, format=None):
    """
    Deletes the pool at `pk`.
    """
    pool = self.get_object(pk)
    pool.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
