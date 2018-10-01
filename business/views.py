# -*- coding: utf8 -*-
from django.utils.timezone import now
from rest_framework import generics

from business.serializers import (CookieSerializer,
                                  ArticleCommentRecordSerializer,
                                  TTUserListSerializer,
                                  ArticleSerializer,
                                  ArticleListSerializer,
                                  ArticleCommentRecordListSerializer)
from business.forms import (TTLoginActionForm,
                            TTCommentActionForm,
                            TTSignedUserListForm,
                            ArticleInputForm,
                            ArticleUpdateForm,
                            ArticleDeleteForm,
                            ArticleDetailForm,
                            ArticleListForm,
                            ArticleCommentRecrodListForm)
from business.models import (TTUser,
                             ArticleCommentRecord,
                             Article)
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
        try:
            serializer = self.post_serializer_class.login_active(validated_data=cld)
        except Exception as e:
            return fm_status.return_error_response(fm_status.HTTP_400_BAD_REQUEST, e.args)
        return fm_status.return_success_response()


ARTICLE_URL_COMPILE = re.compile(r'^https://m.toutiaocdn.cn/group/(\d+)/$|'
                                 r'^https://m.toutiaocdn.com/group/(\d+)/$|'
                                 r'^https://m.toutiaocdn.cn/item/(\d+)/$|'
                                 r'^https://m.toutiaocdn.com/item/(\d+)/$|'
                                 r'^https://m.toutiaocdn.cn/i(\d+)/$|'
                                 r'^https://www.toutiao.com/group/(\d+)/$|'
                                 r'^http://toutiao.com/group/(\d+)/$|'
                                 r'^https://www.toutiao.com/a(\d+)/$')


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
        article_url = kwargs.pop('article_url')
        result = ARTICLE_URL_COMPILE.match(article_url)
        match_list = result.groups()
        group_id = [item for item in match_list if item][0]
        kwargs['group_id'] = group_id
        kwargs['url'] = article_url

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


class TTSignedUserList(FMListAPIView):
    """
    TT登录状态的用户列表
    """
    list_form_class = TTSignedUserListForm
    list_serializer_class = TTUserListSerializer
    model_class = TTUser

    def post(self, request, *args, **kwargs):
        """
        获取TT登录状态的用户列表
        :param request: 
        :param args: 
        :param kwargs: 
        :return: 
        """
        return super(TTSignedUserList, self).post(request, *args, **kwargs)


class ArticleAction(FMActionAPIView):
    """
    文章url、title录入、修改及删除
    """
    post_form_class = ArticleInputForm
    post_serializer_class = ArticleSerializer
    put_form_class = ArticleUpdateForm
    put_serializer_class = ArticleSerializer
    delete_form_class = ArticleDeleteForm
    delete_serializer_class = ArticleSerializer
    model_class = Article

    def post(self, request, *args, **kwargs):
        """
        创建文章
        :param request: 
        :param args: 
        :param kwargs: 
        :return: 
        """
        return super(ArticleAction, self).post(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        """
        更新文章
        :param request: 
        :param args: 
        :param kwargs: 
        :return: 
        """
        return super(ArticleAction, self).put(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """
        删除文章
        :param request: 
        :param args: 
        :param kwargs: 
        :return: 
        """
        return super(ArticleAction, self).delete(request, *args, **kwargs)


class ArticleDetail(FMDetailAPIView):
    """
    文章详情
    """
    detail_form_class = ArticleDetailForm
    detail_serializer_class = ArticleSerializer
    model_class = Article

    def post(self, request, *args, **kwargs):
        """
        获取文章详情
        :param request: 
        :param args: 
        :param kwargs: 
        :return: 
        """
        return super(ArticleDetail, self).post(request, *args, **kwargs)


class ArticleList(FMListAPIView):
    """
    获取文章详情列表
    """
    list_form_class = ArticleListForm
    list_serializer_class = ArticleListSerializer
    model_class = Article

    def post(self, request, *args, **kwargs):
        """
        获取文章详情列表
        :param request: 
        :param args: 
        :param kwargs: 
        :return: 
        """
        return super(ArticleList, self).post(request, *args, **kwargs)


class ArticleCommentRecordList(FMListAPIView):
    """
    获取文章评论列表
    """
    list_form_class = ArticleCommentRecrodListForm
    list_serializer_class = ArticleCommentRecordListSerializer
    model_class = ArticleCommentRecord

    def get_instances_list(self, request, **kwargs):
        return self.model_class.filter_details(**kwargs)

    def post(self, request, *args, **kwargs):
        """
        获取文章评论列表
        :param request: 
        :param args: 
        :param kwargs: 
        :return: 
        """
        return super(ArticleCommentRecordList, self).post(request, *args, **kwargs)
