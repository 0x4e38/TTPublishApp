# -*- coding:utf8 -*-

DEBUG = True

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'oauth2_provider',
    'users',
    'business',

    'rest_framework_swagger',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'TT_BZ',
        'USER': 'yinShi_project',
        'PASSWORD': 'Con!082%Trib*HLie810283*(#2Exdwd3eifqonfI)*&#@C',
        'HOST': '127.0.0.1',
        'PORT': 3306,
    },
}

# 缓存服务器配置
REDIS_SETTINGS = {
    'host': '127.0.0.1',
    'port': 6379,
    'db_set': {
        'business': 0,
        'consumer': 1,
        }
}
