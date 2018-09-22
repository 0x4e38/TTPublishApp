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


class RequestPublicParams(BaseModelMixin, models.Model):
    """
    请求公共参数
    """
    phone = models.CharField('手机号', max_length=16, unique=True)

    ab_client = models.CharField('ab_client', max_length=64)
    ab_feature = models.CharField('ab_feature', max_length=32)
    ab_group = models.CharField('ab_group', max_length=32)
    ab_version = models.TextField('ab_version')
    ac = models.CharField('网络类型', max_length=32)
    aid = models.CharField('aid', max_length=32)
    app_name = models.CharField('app_name', max_length=32)
    as_ = models.CharField('as', max_length=32)

    channel = models.CharField('channel', max_length=32)
    device_id = models.CharField('device_id', max_length=32)
    device_platform = models.CharField('device_platform', max_length=32)
    device_type = models.CharField('device_type', max_length=32)
    idfa = models.CharField('idfa', max_length=64)
    idfv = models.CharField('idfv', max_length=64)
    iid = models.CharField('iid', max_length=32)
    openudid = models.CharField('openudid', max_length=64)

    os_version = models.CharField('os_version', max_length=32)
    resolution = models.CharField('resolution', max_length=32)
    ssmix = models.CharField('ssmix', max_length=32)
    tma_jssdk_version = models.CharField('tma_jssdk_version', max_length=32)
    ts = models.CharField('ts', max_length=32)
    update_version_code = models.CharField('update_version_code', max_length=32)
    version_code = models.CharField('version_code', max_length=32)
    vid = models.CharField('vid', max_length=64)

    class Meta:
        db_table = 'tt_request_public_params'

    def __unicode__(self):
        return self.app_name

    @property
    def perfect_detail(self):
        detail = super(RequestPublicParams, self).perfect_detail
        # "as"字段和python关键字重复
        detail['as'] = detail.pop('as_')
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
        detail.pop('phone')
        return '%s?%s' % (call_url, urllib.urlencode(detail))


class Cookie(BaseModelMixin, models.Model):
    """
    Cookie信息
    """
    phone = models.CharField('手机号', max_length=16, unique=True)

    UM_distinctid = models.CharField('UM_distinctid', max_length=128)
    alert_coverage = models.CharField('alert_coverage', max_length=16)
    install_id = models.CharField('install_id', max_length=32)
    odin_tt = models.CharField('odin_tt', max_length=128)
    sessionid = models.CharField('sessionid', max_length=64)
    sid_guard = models.CharField('sid_guard', max_length=128)
    sid_tt = models.CharField('sid_tt', max_length=64)
    ttreq = models.CharField('ttreq', max_length=64)
    uid_tt = models.CharField('uid_tt', max_length=64)

    class Meta:
        db_table = 'tt_cookie'

    def __unicode__(self):
        return '%s' % self.phone


class Token(BaseModelMixin, models.Model):
    """
    Token信息
    """
    phone = models.CharField('手机号', max_length=16, unique=True)

    token = models.CharField('token字符串', max_length=128)

    class Meta:
        db_table = 'tt_token'

    def __unicode__(self):
        return '%s' % self.phone


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
    def make_tt_http_header(cls, phone):
        cookie_detail = Cookie.get_detail(phone=phone)

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
        token_detail = Token.get_detail(phone=phone)
        http_header_dict = copy.copy(cls.http_header_dict)
        http_header_dict['Cookie'] = cookie_string
        http_header_dict['X-SS-Cookie'] = x_ss_cookie_string
        http_header_dict['tt-request-time'] = '%s' % make_millisecond_time_stamp()
        http_header_dict['x-Tt-Token'] = token_detail['token']
        http_header_dict['x-ss-sessionid'] = cookie_detail['sessionid']
        return http_header_dict

