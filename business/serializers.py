# -*- coding:utf8 -*-
from rest_framework import serializers
from django.conf import settings

from business.models import (Cookie,
                             Token,
                             RequestPublicParams,
                             HttpHeaderAction,
                             TTUser,
                             ArticleCommentRecord)
from business.configs import (APP_REQUEST_PARAMS,
                              APP_REQUEST_URLS,
                              make_perfect_tt_security_string)
from horizon.models import model_to_dict
from horizon import main
from horizon.serializers import (BaseListSerializer,
                                 BaseModelSerializer,
                                 BaseSerializer,
                                 timezoneStringTostring)

from horizon.http_requests import send_http_request

import urllib
import os
import json
import re
import copy
import re


class CookieSerializer(BaseModelSerializer):
    cookie_fields = ('odin_tt', 'sessionid', 'uid_tt', 'sid_tt', 'install_id',
                     'alert_coverage', 'ttreq', 'UM_distinctid', 'sid_guard',
                     'tt_user_id')
    contant_cookie_dict = {
        'UM_distinctid': '165e0b539854d3-09cfd48005b33d8-75460e45-4a574-165e0b539868d4',
        'alert_coverage': '93',
        'install_id': '44173039849',
        'ttreq': '1$4fe98fbd2356099daa5c2fe90233f0f2c09a852e',
    }
    _p_errors = None
    phone = None
    email = None
    tt_token = None
    tt_user_info = None
    tt_user_id = None

    def __init__(self, instance=None, data=None, request=None, **kwargs):
        if data:
            self.phone = data.get('phone')
            self.email = data.get('email')

            validated_data = {key: '' for key in self.cookie_fields}
            result = self.login_to_tt(data)
            response_json = json.loads(result.text)
            if isinstance(result, Exception) or response_json['message'] != 'success':
                self._p_errors = 'Login TT failed'
            else:
                # 登录成功
                # headers 数据样式
                # {'Connection': 'keep-alive',
                #  'Content-Encoding': 'gzip',
                #  'Content-Type': 'application/json',
                #  'Date': 'Sat, 22 Sep 2018 09:54:12 GMT',
                #  'Server': 'nginx',
                #  'Set-Cookie': 'odin_tt=6b3fa0f7c8702309c6ac206f5329db7360c65240c5e1d78ca36bdd866ad3f1dc4a9269be8be1ba75d1b8e1c631463ec1; Path=/; Domain=snssdk.com; Max-Age=86400000, sid_guard=23f79bad721a8c4d5630f1afd3321d83%7C1537610052%7C5184000%7CWed%2C+21-Nov-2018+09%3A54%3A12+GMT; Path=/; Domain=snssdk.com; Max-Age=31104000; HttpOnly, uid_tt=d6e00f73fdb789d002aa7b6cb3531433; Path=/; Domain=snssdk.com; Max-Age=5184000; HttpOnly, sid_tt=23f79bad721a8c4d5630f1afd3321d83; Path=/; Domain=snssdk.com; Max-Age=5184000; HttpOnly, sessionid=23f79bad721a8c4d5630f1afd3321d83; Path=/; Domain=snssdk.com; Max-Age=5184000; HttpOnly',
                #  'Transfer-Encoding': 'chunked',
                #  'Vary': 'Accept-Encoding, Origin, Accept-Encoding, Accept-Encoding, Accept-Encoding',
                #  'X-SS-Set-Cookie': 'odin_tt=6b3fa0f7c8702309c6ac206f5329db7360c65240c5e1d78ca36bdd866ad3f1dc4a9269be8be1ba75d1b8e1c631463ec1; Path=/; Domain=snssdk.com; Max-Age=86400000, sid_guard=23f79bad721a8c4d5630f1afd3321d83%7C1537610052%7C5184000%7CWed%2C+21-Nov-2018+09%3A54%3A12+GMT; Path=/; Domain=snssdk.com; Max-Age=31104000; HttpOnly, uid_tt=d6e00f73fdb789d002aa7b6cb3531433; Path=/; Domain=snssdk.com; Max-Age=5184000; HttpOnly, sid_tt=23f79bad721a8c4d5630f1afd3321d83; Path=/; Domain=snssdk.com; Max-Age=5184000; HttpOnly, sessionid=23f79bad721a8c4d5630f1afd3321d83; Path=/; Domain=snssdk.com; Max-Age=5184000; HttpOnly',
                #  'X-TT-LOGID': '20180922175412010020078144619D52',
                #  'X-TT-TIMESTAMP': '1537610052.696',
                #  'X-Tt-Token': '0023f79bad721a8c4d5630f1afd3321d831f853906ffd4861989e6caa0bc60382ce2fe8c9cd70c0dcd7cb58299740327467',
                #  'X-Tt-Token-Sign': 'a7a046775dd8c105a5ab263dbae8b146ee1e353a3ba327b92511c066bac34f8635e38a979a5ffee3d6521e218d3483a2b68fee1113ef0304b59eb6543a8662b56ca7f88376aff320cf656b4bb737cedf3aab6165a96e10a8cafafb502e1bd995fe6cf534a3cdcb3ecd676e81c15db19e111d83da31c9a63fd5d8548cd043d1c3'
                # }
                # set cookie
                header_dict = dict(result.headers)
                re_com = re.compile(r'[^,]*?=[^,]*?;')
                set_cookie_list = [item.strip() for item in re_com.findall(header_dict['set-cookie'])]
                set_cookie_list = [item.strip(';').split('=') for item in set_cookie_list]
                self.tt_token = header_dict['x-tt-token']
                self.tt_user_info = response_json
                self.tt_user_id = response_json['data']['user_id']

                opts = self.Meta.model._meta
                fields = [f.name for f in opts.concrete_fields]
                validated_data = {}
                for key, value in set_cookie_list:
                    if key in fields:
                        validated_data[key] = value

                validated_data.update(**self.contant_cookie_dict)
                validated_data.update(**{'tt_user_id': self.tt_user_id})

            cookie_instance = Cookie.get_object(tt_user_id=self.tt_user_id)
            if isinstance(cookie_instance, Exception):
                super(CookieSerializer, self).__init__(data=validated_data, **kwargs)
            else:
                super(CookieSerializer, self).__init__(instance, **kwargs)
        else:
            super(CookieSerializer, self).__init__(instance, **kwargs)

    class Meta:
        model = Cookie
        fields = '__all__'

    @property
    def errors(self):
        if self._p_errors:
            return self._p_errors
        else:
            return super(CookieSerializer, self).errors

    def login_to_tt(self, data):
        login_info_dict = {
            # 手机号、验证码登录
            'phone_identifying_code': {
                'login_info': APP_REQUEST_URLS['login_mobile'],
                'login_params': APP_REQUEST_PARAMS['login_mobile']
            },
            # 手机号、密码登录
            'phone_password': {
                'login_info': APP_REQUEST_URLS['login_mobile_password'],
                'login_params': APP_REQUEST_PARAMS['login_mobile_password']
            },
            # 邮箱、密码登录
            'email_password': {
                'login_info': APP_REQUEST_URLS['login_email'],
                'login_params': APP_REQUEST_PARAMS['login_email']
            }
        }
        params_info_dict = {
            'phone_identifying_code': ('mobile', 'code'),
            'phone_password': ('mobile', 'password'),
            'email_password': ('email', 'password'),
        }

        account = data['phone'] if data['login_type'].startswith('phone') else data['email']
        login_info = login_info_dict[data['login_type']]
        # 向TT发送登录请求
        call_url = RequestPublicParams.get_perfect_url_with_query_string(
            phone=self.phone,
            call_url=login_info['login_info']['url']
        )
        params = copy.copy(login_info['login_params'])
        params[params_info_dict[data['login_type']][0]] = make_perfect_tt_security_string(account)
        params[params_info_dict[data['login_type']][1]] = make_perfect_tt_security_string(data['password'])

        header = HttpHeaderAction.make_tt_http_header(account=account)
        result = send_http_request(access_url=call_url,
                                   access_params=params,
                                   method=login_info['login_info']['method'],
                                   headers=header,
                                   verify=False)
        return result

    def update_token_and_user(self, **kwargs):
        # 新建或更新token
        token_data = {'tt_user_id': self.tt_user_id,
                      'token': self.tt_token}
        TokenSerializer.save_token(token_data)

        # 新建或更新tt user
        user_data = {'user_id': self.tt_user_id,
                     'name': self.tt_user_info['data']['name'],
                     'phone': self.phone,
                     'email': self.email}
        TTUserSerializer.save_user(user_data)

    @classmethod
    def login_active(cls, validated_data):
        serializer = cls(data=validated_data)

        serializer.update_token_and_user()
        if not serializer.instance:
            if not serializer.is_valid():
                raise Exception(serializer.errors)
            return serializer.save()
        else:
            validated_data.pop('tt_user_id')
            return serializer.update(serializer.instance, validated_data)


class TokenSerializer(BaseModelSerializer):
    def __init__(self, instance=None, data=None, **kwargs):
        if data:
            instance = self.Meta.model.get_object(tt_user_id=data['tt_user_id'])
            if isinstance(instance, Exception):
                super(TokenSerializer, self).__init__(data=data, **kwargs)
            else:
                super(TokenSerializer, self).__init__(instance, **kwargs)
        else:
            super(TokenSerializer, self).__init__(instance, **kwargs)

    class Meta:
        model = Token
        fields = '__all__'

    @classmethod
    def save_token(cls, validated_data):
        serializer = cls(data=validated_data)
        if not serializer.instance:
            if not serializer.is_valid():
                raise Exception(serializer.errors)
            return serializer.save()
        else:
            validated_data.pop('tt_user_id')
            return serializer.update(serializer.instance, validated_data)

    # def save(self, **kwargs):
    #     instance = self.Meta.model.get_object(tt_user_id=self.validated_data['tt_user_id'])
    #     # 新建token
    #     if isinstance(instance, Exception):
    #         return super(TokenSerializer, self).save()
    #     else:
    #         # 更新token
    #         self.instance = instance
    #         return super(TokenSerializer, self).update(instance, self.validated_data)


class TTUserSerializer(BaseModelSerializer):
    def __init__(self, instance=None, data=None, **kwargs):
        if data:
            instance = self.Meta.model.get_object(user_id=data['user_id'])
            if isinstance(instance, Exception):
                super(TTUserSerializer, self).__init__(data=data, **kwargs)
            else:
                super(TTUserSerializer, self).__init__(instance, **kwargs)
        else:
            super(TTUserSerializer, self).__init__(instance, **kwargs)

    class Meta:
        model = TTUser
        fields = '__all__'

    @classmethod
    def save_user(cls, validated_data):
        serializer = cls(data=validated_data)
        if not serializer.instance:
            if not serializer.is_valid():
                raise Exception(serializer.errors)
            return serializer.save()
        else:
            validated_data.pop('user_id')
            return serializer.update(serializer.instance, validated_data)

    # def save(self, **kwargs):
    #     instance = self.Meta.model.get_object(user_id=self.validated_data['user_id'])
    #     # 新建token
    #     if isinstance(instance, Exception):
    #         return super(TTUserSerializer, self).save()
    #     else:
    #         # 更新token
    #         self.instance = instance
    #         return super(TTUserSerializer, self).update(instance, self.validated_data)


class ArticleCommentRecordSerializer(BaseModelSerializer):
    def __init__(self, instance=None, data=None, request=None, **kwargs):
        if data:
            # 发表评论
            result = self.comment_to_tt(data)
            response_json = json.loads(result.text)
            if isinstance(result, Exception) or response_json['message'] != 'success':
                self._p_errors = 'Comment to TT failed'

            super(ArticleCommentRecordSerializer, self).__init__(data=data, **kwargs)
        else:
            super(ArticleCommentRecordSerializer, self).__init__(instance, **kwargs)

    class Meta:
        model = ArticleCommentRecord
        fields = '__all__'

    def comment_to_tt(self, data):
        comment_url_info = APP_REQUEST_URLS['comment']
        comment_params = APP_REQUEST_PARAMS['comment']

        # 向TT发送登录请求
        call_url = RequestPublicParams.get_perfect_url_with_query_string(
            phone=None,
            call_url=comment_url_info['url']
        )
        params = copy.copy(comment_params)
        params['comment_duration'] = params['comment_duration']()
        params['content'] = data['comment_content']
        params['group_id'] = data['group_id']
        params['item_id'] = data['group_id']
        params['staytime_ms'] = params['staytime_ms']()
        params['text'] = data['comment_content']

        header = HttpHeaderAction.make_tt_http_header(tt_user_id=data['tt_user_id'])
        result = send_http_request(access_url=call_url,
                                   access_params=params,
                                   method=comment_url_info['method'],
                                   headers=header,
                                   verify=False)
        return result
