# -*- coding: utf8 -*-
from rest_framework import viewsets
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from oauth2_provider.views import TokenView
from oauth2_provider.models import AccessToken
from django.utils.timezone import now
from django.http.response import HttpResponse

from users.serializers import (UserSerializer,)
from users.permissions import IsOwnerOrReadOnly
from users.models import (BusinessUser,
                          make_token_expire)
from users.forms import UserDetailForm

from horizon.views import (APIView,
                           FMDetailAPIView,
                           FMActionAPIView,
                           FMListAPIView)
from horizon import main
from horizon.http import status as fm_status

import copy
import urllib
import json


class AuthLogin(TokenView):
    def set_old_token_to_expires(self, new_token):
        token = AccessToken.objects.get(token=new_token)
        kwargs = {'user': token.user, 'id__lt': token.id, 'expires__gt': now()}
        expires_token_list = AccessToken.objects.filter(**kwargs)
        for expires_token in expires_token_list:
            expires_token.expires = now()
            expires_token.save()

    def post(self, request, *args, **kwargs):
        response = super(AuthLogin, self).post(request, *args, **kwargs)
        response_dict = json.loads(response.content)

        if response.status_code == 200:
            # 单点登录
            self.set_old_token_to_expires(response_dict['access_token'])
            return_dict = {'code': 200,
                           'message': 'ok',
                           'data': response_dict}
        else:
            return_dict = {'code': response.status_code,
                           'message': response_dict}
        return HttpResponse(json.dumps(return_dict), 'text/plain')


class AuthLogout(generics.GenericAPIView):
    """
    用户认证：登出
    """
    def post(self, request, *args, **kwargs):
        make_token_expire(request)
        return Response(status=status.HTTP_200_OK)


class UserDetail(FMDetailAPIView):
    """
    获取哦用户详情
    """
    detail_form_class = UserDetailForm
    detail_serializer_class = UserSerializer
    model_class = BusinessUser

    def get_instance(self, request, **kwargs):
        return self.model_class.get_object(**{'pk': request.user.id})

    def post(self, request, *args, **kwargs):
        """
        获取用户详情
        :param request: 
        :param args: 
        :param kwargs: 
        :return: 
        """
        return super(UserDetail, self).post(request, *args, **kwargs)
