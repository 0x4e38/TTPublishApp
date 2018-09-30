# -*- coding: utf8 -*-
from django.utils.timezone import now
from rest_framework import generics

from business.serializers import (CookieSerializer,
                                  ArticleCommentRecordSerializer)
from business.forms import (TTLoginActionForm,
                            TTCommentActionForm)
from business.models import (TTUser,
                             ArticleCommentRecord)
from horizon.views import (FMActionAPIView,
                           FMDetailAPIView,
                           FMListAPIView)
from horizon.http import status as fm_status

from horizon import main

import json
import random
import re


class TTLoginAction(generics.GenericAPIView):
    """
    TT登录
    """
    post_form_class = TTLoginActionForm
    post_serializer_class = CookieSerializer
    model_class = None

    def is_request_data_valid(self, **kwargs):
        if kwargs['login_type'].startswith('phone'):
            if not kwargs.get('phone'):
                return False, 'Phone is must not be empty when [login_type] is ' \
                              '"phone_identifying_code" or "phone_password"'
        elif kwargs['login_type'].startswith('email'):
            if not kwargs.get('email'):
                return False, 'Email is must not be empty when [login_type] is ' \
                              '"email_password"'
        return True, None

    def post(self, request, *args, **kwargs):
        """
        创建数据
        :param request: 
        :param args: 
        :param kwargs: 
        :return: 
        """
        if not (self.post_form_class or self.post_serializer_class):
            return fm_status.return_error_response(fm_status.HTTP_405_METHOD_NOT_ALLOWED)

        form = self.post_form_class(request.data, request.FILES)
        if not form.is_valid():
            return fm_status.return_error_response(fm_status.HTTP_400_BAD_REQUEST, form.errors)

        cld = form.cleaned_data
        is_valid, error_message = self.is_request_data_valid(**cld)
        if not is_valid:
            return fm_status.return_error_response(fm_status.HTTP_400_BAD_REQUEST, error_message)

        serializer = self.post_serializer_class.login_active(validated_data=cld)
        if not serializer.is_valid():
            return fm_status.return_error_response(fm_status.HTTP_400_BAD_REQUEST, serializer.errors)
        try:
            serializer.save()
        except Exception as e:
            return fm_status.return_error_response(fm_status.HTTP_400_BAD_REQUEST, e.args)
        return fm_status.return_success_response()


ARTICLE_URL_COMPILE = re.compile(r'^http://toutiao.com/group/(\d+)/$')


class TTCommentAction(FMActionAPIView):
    """
    TT评论
    """
    post_form_class = TTCommentActionForm
    post_serializer_class = ArticleCommentRecordSerializer
    model_class = ArticleCommentRecord

    def is_request_data_valid(self, **kwargs):
        article_url = kwargs['article_url']
        result = ARTICLE_URL_COMPILE.match(article_url)
        if not result:
            return False, 'Article url is incorrect!'
        return True, None

    def get_perfect_request_data(self, **kwargs):
        article_url = kwargs['article_url']
        result = ARTICLE_URL_COMPILE.match(article_url)
        kwargs['group_id'] = result.group(1)
        return kwargs

    def post(self, request, *args, **kwargs):
        """
        TT发表评论
        :param request: 
        :param args: 
        :param kwargs: 
        :return: 
        """
        return super(TTCommentAction, self).post(request, *args, **kwargs)
