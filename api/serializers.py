# from api.models import Pool, Team
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.authtoken.models import Token


class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ('username', 'email', 'password')
    extra_kwargs = {'password': {'write_only': True}}
    read_only_fields = (
      'is_staff',
      'is_superuser',
      'is_active',
      'date_joined',
    )

  def create(self, validated_data):
    from api import shravan
    shravan.SAY('validated data: %s' % validated_data)
    user = User(
        email=validated_data['email'],
        username=validated_data['username'],
    )
    user.set_password(validated_data['password'])
    user.save()

    # Create a Token for this user
    token = Token.objects.create(user=user)
    shravan.SAY('token: %s' % token)

    return user


# class PoolSerializer(serializers.HyperlinkedModelSerializer):
#   class Meta:
#     model = Pool
#     fields = ('id', 'name')


# class TeamSerializer(serializers.ModelSerializer):
#     class Meta:
#       model = Team
#       fields = ('id', 'name', 'short_name')
