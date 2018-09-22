# -*- coding:utf8 -*-
from rest_framework import serializers
from django.conf import settings

from business.models import (Cookie,
                             Token,
                             RequestPublicParams,
                             HttpHeaderAction)
from business.configs import (APP_REQUEST_PARAMS,
                              APP_REQUEST_URLS)
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
    contant_cookie_dict = {
        'UM_distinctid': '165e0b539854d3-09cfd48005b33d8-75460e45-4a574-165e0b539868d4',
        'alert_coverage': '93',
        'install_id': '44173039849',
        'ttreq': '1$4fe98fbd2356099daa5c2fe90233f0f2c09a852e',
    }
    _p_errors = None
    phone = None

    def __init__(self, instance=None, data=None, **kwargs):
        if data:
            self.phone = data['phone']
            # 向TT发送登录请求
            call_url = RequestPublicParams.get_perfect_url_with_query_string(
                phone=self.phone,
                call_url=APP_REQUEST_URLS['login']['url']
            )
            params = copy.copy(APP_REQUEST_PARAMS['login'])
            params['code'] = data['identifying_code']
            params['mobile'] = self.phone

            validated_data = {}
            header = HttpHeaderAction.make_tt_http_header(phone=self.phone)
            result = send_http_request(access_url=call_url,
                                       access_params=params,
                                       method=APP_REQUEST_URLS['login']['method'],
                                       headers=header)
            if isinstance(result, Exception) or result.text['message'] != 'success':
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
                #  'X-Tt-Token-Sign': 'a7a046775dd8c105a5ab263dbae8b146ee1e353a3ba327b92511c066bac34f8635e38a979a5ffee3d6521e218d3483a2b68fee1113ef0304b59eb6543a8662b56ca7f88376aff320cf656b4bb737cedf3aab6165a96e10a8cafafb502e1bd995fe6cf534a3cdcb3ecd676e81c15db19e111d83da31c9a63fd5d8548cd043d1c3'}
                # set cookie
                header_dict = dict(result.headers)
                re_com = re.compile(r'[^,]*?=[^,]*?;')
                set_cookie_list = [item.strip() for item in re_com.findall(header_dict['Set-Cookie'])]
                set_cookie_list = [item.strip(';').split('=') for item in set_cookie_list]

                opts = self.Meta.model._meta
                fields = [f.name for f in opts.concrete_fields]
                validated_data = {}
                for key, value in set_cookie_list:
                    if key in fields:
                        validated_data[key] = value

            super(CookieSerializer, self).__init__(data=validated_data, **kwargs)
        else:
            super(CookieSerializer, self).__init__(instance, **kwargs)

    class Meta:
        model = Cookie
        field = '__all__'

    @property
    def errors(self):
        if self._p_errors:
            return self._p_errors
        else:
            return super(CookieSerializer, self).errors

    def save(self, **kwargs):
        cookie_instance = Cookie.get_object(phone=self.phone)
        # 新建cookie
        if isinstance(cookie_instance, Exception):
            kwargs.update(**self.contant_cookie_dict)
            return super(CookieSerializer, self).save(**kwargs)
        else:
            # 更新cookie
            return super(CookieSerializer, self).update(cookie_instance, self.validated_data)
