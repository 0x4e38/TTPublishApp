# -*- coding:utf8 -*-

import os


# 数字和字符串对应关系
TT_NUMBER_AND_STRING_MAPPING = {
    '0': '35',
    '1': '34',
    '2': '37',
    '3': '36',
    '4': '31',
    '5': '30',
    '6': '33',
    '7': '32',
    '8': '3d',
    '9': '3c',
}

# TT web请求gateway（用户相关：登录、用户信息等）
APP_SECURITY_API_GATEWAY = 'https://security.snssdk.com/'

# web请求参数配置
APP_REQUEST_PARAMS = {
    'login': {
        'code': None,
        'mobile': None,
    },
}

# web请求URL配置
APP_REQUEST_URLS = {
    'login': {
        'url': os.path.join(APP_SECURITY_API_GATEWAY, 'passport/mobile/sms_login/'),
        'method': 'post',
    },
    'get_user_info': {
        'url': os.path.join(APP_SECURITY_API_GATEWAY, '2/user/info/'),
        'method': 'get',
    }
}


