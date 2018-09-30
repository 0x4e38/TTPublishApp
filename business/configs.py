# -*- coding:utf8 -*-

from horizon.main import get_random_millisecond
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
    '@': '45',
    'q': '74',
    '.': '2b',
    'c': '66',
    'o': '6a',
    'm': '68',
    'z': '7f',
    'h': '6d',
    'a': '64',
    'n': '6b',
    'g': '62',
    '*': '2f',
}


def make_perfect_tt_security_string(source_string):
    """
    生成加密字符串
    :param source_string: 源字符串
    :return: 加密后的字符串
    """
    item_list = []
    for char in source_string:
        item_list.append(TT_NUMBER_AND_STRING_MAPPING.get(char, '00'))
    return ''.join(item_list)


# TT web请求gateway（用户相关：登录、用户信息等）
APP_SECURITY_API_GATEWAY = 'https://security.snssdk.com/'

# TT web请求gateway（发表评论、点赞相关等）
APP_ARTICLE_ACTION_API_GATEWAY = 'https://is.snssdk.com/'

# web请求参数配置
APP_REQUEST_PARAMS = {
    'login_mobile': {
        'mobile': None,
        'code': None,
    },
    'login_mobile_password': {
        'mobile': None,
        'password': None,
    },
    'login_email': {
        'email': None,
        'password': None,
    },
    'comment': {
        'aggr_type': 1,
        'comment_duration': get_random_millisecond,  # 评论持续时间
        'content': None,           # 评论内容
        'group_id': None,          # 文章组ID
        'is_comment': 1,           # 是否评论
        'item_id': None,           # 文章ID
        'mention_concern': '',
        'mention_user': '',
        'platform': '',
        'read_pct': 100,
        'repost': 0,
        'share_tt': 0,
        'staytime_ms': get_random_millisecond,       # 停留时间
        'text': None,              # 评论内容
        'text_rich_span': '{}',
        'zz': 0,
    }
}

# web请求URL配置
APP_REQUEST_URLS = {
    'login_mobile': {
        'url': os.path.join(APP_SECURITY_API_GATEWAY, 'passport/mobile/sms_login/'),
        'method': 'post',
    },
    'login_mobile_password': {
        'url': os.path.join(APP_SECURITY_API_GATEWAY, ' passport/mobile/login'),
        'method': 'post',
    },
    'login_email': {
        'url': os.path.join(APP_SECURITY_API_GATEWAY, 'user/auth/email_login/'),
        'method': 'post',
    },
    'get_user_info': {
        'url': os.path.join(APP_SECURITY_API_GATEWAY, '2/user/info/'),
        'method': 'get',
    },
    'comment': {
        'url': os.path.join(APP_ARTICLE_ACTION_API_GATEWAY, '2/data/v5/post_message/'),
        'method': 'post',
    }
}


