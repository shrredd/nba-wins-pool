# from api.models import Pool
from api.permissions import IsStaffOrTargetUser
from api.serializers import UserSerializer
from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

import logging
logger = logging.getLogger('testlogger')
logger.info('blah de blah')

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    # queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    model = User
    queryset = User.objects.all()
    lookup_field = ('username')

    def create(self, request):
      from api import shravan
      logger.info('request data: %s' % request.data)
      serializer = UserSerializer(data=request.data)
      if serializer.is_valid():
        logger.info('serializer is valid...')
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
      logger.info('serializer says john is invalid')
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, format=None):
      users = User.objects.all()
      serializer = UserSerializer(users, many=True)
      return Response(serializer.data)

    def post(self, request, format=None):
      logger.info('request: %s' % request)
      super(UserViewSet, self).post(request, format=format)
    #     serializer = UserSerializer(data=request.DATA)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        user = self.get_object(pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_permissions(self):
      from api import shravan
      shravan.SAY('get permissions called....')
      # allow non-authenticated user to create via POST
      return (AllowAny() if self.request.method == 'POST'
                else IsStaffOrTargetUser()),

# class PoolsByUserViewSet(generics.ListAPIView):
#     serializer_class = PoolSerializer

#     def get_queryset(self):
#         """
#         This view should return a list of all the pools
#         for the currently authenticated user.
#         """
#         user = self.request.user
#         return Pool.objects.filter(user=user)
