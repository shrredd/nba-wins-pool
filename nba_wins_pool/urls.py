"""nba_wins_pool URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

import logging

from api import views
from django.conf.urls import url, include
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'accounts', views.UserViewSet)
# router.register(r'pools', views.PoolViewSet)

logger = logging.getLogger('nba-logger')

logger.info('all router urls: %s' % router.urls)
# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^api/v1/', include(router.urls)),

    # Details of Pools
    url(r'^api/v1/pools/(?P<pool_id>[0-9]+)$', views.PoolDetail.as_view()),
    url(r'^api/v1/pools/(?P<pool_id>[0-9]+)/draft/', views.DraftDetail.as_view()),
    url(r'^api/v1/pools/(?P<pool_id>[0-9]+)/members/', views.PoolMembers.as_view()),

    url(r'^api/v1/(?P<username>[a-zA-Z]+)/pools/', views.PoolsByUser.as_view()),
    url(r'^api/v1/auth/', obtain_auth_token),

    # TODO(shravan): Remove this in production.
    # DEBUGGING ONLY
    url(r'^api/v1/pools/$', views.PoolList.as_view()),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
