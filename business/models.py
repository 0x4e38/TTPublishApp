# -*- coding:utf8 -*-
from django.db import models, transaction
from django.utils.timezone import now
from django.contrib.auth.hashers import make_password
from oauth2_provider.models import AccessToken

from horizon.models import (model_to_dict,
                            BaseExpiresManager,
                            BaseManager)
from horizon.main import (minutes_15_plus,
                          minutes_5_plus,
                          make_millisecond_time_stamp)
from horizon.mixins import BaseModelMixin

import datetime
import re
import os
import urllib
import time
import copy


class TTUser(BaseModelMixin, models.Model):
    """
    TT user信息
    """
    user_id = models.BigIntegerField(u'TT user id', unique=True)
    name = models.CharField(u'昵称', max_length=128, null=True, blank=True)
    phone = models.CharField(u'手机号', max_length=16, unique=True, null=True)
    email = models.EmailField(u'邮箱',  max_length=128, unique=True, null=True)
    password_for_phone = models.CharField(u'手机登录密码', max_length=64, null=True)
    password_for_email = models.CharField(u'邮箱登录密码', max_length=64, null=True)
    created = models.DateTimeField(u'创建时间', default=now)
    updated = models.DateTimeField(u'更新时间', auto_now=True)

    class Meta:
        db_table = 'tt_auth_user'

    def __unicode__(self):
        return self.user_id

    @classmethod
    def get_user_detail(cls, account):
        """
        获取TT用户信息
        :param account: 手机号或邮箱
        :return: tt user info dict
        """
        # 邮箱
        if '@' in account:
            return cls.get_detail(email=account)
        # 手机号
        else:
            return cls.get_detail(phone=account)


class RequestPublicParams(BaseModelMixin, models.Model):
    """
    请求公共参数
    """
    phone = models.CharField(u'手机号', max_length=16, unique=True)

    ab_client = models.CharField(u'ab_client', max_length=64)
    ab_feature = models.CharField(u'ab_feature', max_length=32)
    ab_group = models.CharField(u'ab_group', max_length=32)
    ab_version = models.TextField(u'ab_version')
    ac = models.CharField(u'网络类型', max_length=32)
    aid = models.CharField(u'aid', max_length=32)
    app_name = models.CharField(u'app_name', max_length=32)
    app_id = models.CharField(u'app_id', max_length=32)
    _as = models.CharField(u'as', max_length=32)

    channel = models.CharField(u'channel', max_length=32)
    device_id = models.CharField(u'device_id', max_length=32)
    device_platform = models.CharField(u'device_platform', max_length=32)
    device_type = models.CharField(u'device_type', max_length=32)
    fp = models.CharField(u'fp', max_length=64, default='')
    idfa = models.CharField(u'idfa', max_length=64)
    idfv = models.CharField(u'idfv', max_length=64)
    iid = models.CharField(u'iid', max_length=32)
    openudid = models.CharField(u'openudid', max_length=64)

    os_version = models.CharField(u'os_version', max_length=32)
    resolution = models.CharField(u'resolution', max_length=32)
    ssmix = models.CharField(u'ssmix', max_length=32)
    tma_jssdk_version = models.CharField(u'tma_jssdk_version', max_length=32)
    ts = models.CharField(u'ts', max_length=32)
    update_version_code = models.CharField(u'update_version_code', max_length=32)
    version_code = models.CharField(u'version_code', max_length=32)
    vid = models.CharField(u'vid', max_length=64)
    vendor_id = models.CharField(u'vendor_id', max_length=64)
    mix_mode = models.CharField(u'mix_mode', max_length=16)
    install_id = models.CharField(u'install_id', max_length=16)

    class Meta:
        db_table = 'tt_request_public_params'

    def __unicode__(self):
        return self.app_name

    @property
    def perfect_detail(self):
        detail = super(RequestPublicParams, self).perfect_detail
        # "as"字段和python关键字重复
        detail['as'] = detail.pop('_as')
        return detail

    @classmethod
    def get_perfect_url_with_query_string(cls, phone, call_url):
        """
        生成带query string的URL
        :param phone: 手机号
        :param call_url: 请求的URL
        :return: 
        """
        detail = cls.get_detail(phone=phone)
        if isinstance(detail, Exception):
            instance = cls.filter_objects(page_size=1, page_index=1)[0]
            detail = instance.perfect_detail
        detail.pop('phone')
        return '%s?%s' % (call_url, urllib.urlencode(detail))


class Token(BaseModelMixin, models.Model):
    """
    Token信息
    """
    tt_user_id = models.BigIntegerField(u'TT user ID', unique=True)
    token = models.CharField(u'token字符串', max_length=128)
    created = models.DateTimeField(u'创建时间', default=now)
    updated = models.DateTimeField(u'更新时间', auto_now=TTUser)

    class Meta:
        db_table = 'tt_token'

    def __unicode__(self):
        return '%s' % self.tt_user_id


class Cookie(BaseModelMixin, models.Model):
    """
    Cookie信息
    """
    tt_user_id = models.BigIntegerField(u'TT user ID', unique=True)

    UM_distinctid = models.CharField(u'UM_distinctid', max_length=128)
    alert_coverage = models.CharField(u'alert_coverage', max_length=16)
    install_id = models.CharField(u'install_id', max_length=32)
    odin_tt = models.CharField(u'odin_tt', max_length=128)
    sessionid = models.CharField(u'sessionid', max_length=64)
    sid_guard = models.CharField(u'sid_guard', max_length=128)
    sid_tt = models.CharField(u'sid_tt', max_length=64)
    ttreq = models.CharField(u'ttreq', max_length=64)
    uid_tt = models.CharField(u'uid_tt', max_length=64)

    class Meta:
        db_table = 'tt_cookie'

    def __unicode__(self):
        return '%s' % self.tt_user_id


class HttpHeaderAction(object):
    """
    TT http header
    """
    http_header_dict = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': 'install_id=44173039849; '
                  'ttreq=1$4fe98fbd2356099daa5c2fe90233f0f2c09a852e; '
                  'alert_coverage=96; '
                  'UM_distinctid=165e0b539854d3-09cfd48005b33d8-75460e45-4a574-165e0b539868d4;'
                  ' qh[360]=1; '
                  'odin_tt=0a6753383092331f0044b133bfbdc467d30a55bb716f834c8f99d11ce1597feaf6790b47bd93ded5852470c8bc4c245a; '
                  'sid_guard=ddbf9810af396b50f450b8576406cdd0%7C1537241091%7C5184000%7CSat%2C+17-Nov-2018+03%3A24%3A51+GMT;'
                  ' uid_tt=c673208182d063b5dae9e2cef11461f0; '
                  'sid_tt=ddbf9810af396b50f450b8576406cdd0; '
                  'sessionid=ddbf9810af396b50f450b8576406cdd0',
        'User-Agent': 'News 6.8.8 rv:6.8.8.24 (iPhone; iOS 12.0; zh_CN) Cronet',
        'X-SS-Cookie': 'qh[360]=1; '
                       'UM_distinctid=165e0b539854d3-09cfd48005b33d8-75460e45-4a574-165e0b539868d4;'
                       ' alert_coverage=96;'
                       ' install_id=44173039849;'
                       ' odin_tt=0a6753383092331f0044b133bfbdc467d30a55bb716f834c8f99d11ce1597feaf6790b47bd93ded5852470c8bc4c245a;'
                       ' sessionid=ddbf9810af396b50f450b8576406cdd0; '
                       'sid_guard=ddbf9810af396b50f450b8576406cdd0%7C1537241091%7C5184000%7CSat%2C+17-Nov-2018+03%3A24%3A51+GMT; '
                       'sid_tt=ddbf9810af396b50f450b8576406cdd0; '
                       'ttreq=1$4fe98fbd2356099daa5c2fe90233f0f2c09a852e; '
                       'uid_tt=c673208182d063b5dae9e2cef11461f0',
        'X-SS-TC': '0',
        'sdk-version': '1',
        'tt-request-time': '1537241848723',
        'x-Tt-Token': '00ddbf9810af396b50f450b8576406cdd0fef05380e7d9d56514477960b6230b1dbeed3e85d45595ff2943d0809d81c1402a',
        'x-ss-sessionid': 'ddbf9810af396b50f450b8576406cdd0'
    }

    cookie_key_list = ('install_id', 'ttreq', 'alert_coverage', 'UM_distinctid', 'qh[360]',
                       'odin_tt', 'sid_guard', 'uid_tt', 'sid_tt', 'sessionid')
    x_ss_cookie_key_list = ('qh[360]', 'UM_distinctid', 'alert_coverage', 'install_id',
                            'odin_tt', 'sessionid', 'sid_guard', 'sid_tt', 'ttreq', 'uid_tt')

    @classmethod
    def make_tt_http_header(cls, tt_user_id=None, account=None):
        if tt_user_id:
            user_info = None
        else:
            user_info = TTUser.get_user_detail(account)

        if isinstance(user_info, Exception):
            cookie_detail = Cookie.filter_details(page_size=1, page_index=1)[0]
            token_detail = Token.filter_details(page_size=1, page_index=1)[0]
        else:
            if user_info:
                tt_user_id = user_info['user_id']
            cookie_detail = Cookie.get_detail(tt_user_id=tt_user_id)
            token_detail = Token.get_detail(tt_user_id=tt_user_id)

        cookie_str_list = []
        for cookie_key in cls.cookie_key_list:
            if cookie_key == 'qh[360]':
                cookie_str_list.append('%s=1' % cookie_key)
            else:
                cookie_str_list.append('%s=%s' % (cookie_key, cookie_detail[cookie_key]))
        x_ss_cookie_str_list = []
        for x_ss_key in cls.x_ss_cookie_key_list:
            if x_ss_key == 'qh[360]':
                x_ss_cookie_str_list.append('%s=1' % x_ss_key)
            else:
                x_ss_cookie_str_list.append('%s=%s' % (x_ss_key, cookie_detail[x_ss_key]))

        cookie_string = '; '.join(cookie_str_list)
        x_ss_cookie_string = '; '.join(x_ss_cookie_str_list)
        http_header_dict = copy.copy(cls.http_header_dict)
        http_header_dict['Cookie'] = cookie_string
        http_header_dict['X-SS-Cookie'] = x_ss_cookie_string
        http_header_dict['tt-request-time'] = '%s' % make_millisecond_time_stamp()
        http_header_dict['x-Tt-Token'] = token_detail['token']
        http_header_dict['x-ss-sessionid'] = cookie_detail['sessionid']
        return http_header_dict


class ArticleCommentRecord(BaseModelMixin, models.Model):
    """
    文章评论记录
    """
    url = models.CharField(u'文章url', max_length=256)
    group_id = models.CharField(u'文章group id', max_length=128)
    tt_user_id = models.BigIntegerField(u'tt user id')
    content = models.CharField(u'评论内容', max_length=256)
    created = models.DateTimeField(u'创建时间', default=now)
    updated = models.DateTimeField(u'更新时间', auto_now=True)

    class Meta:
        db_table = 'tt_article_comment_record'

    def __unicode__(self):
        return '%s: %s' % (self.tt_user_id, self.group_id)

