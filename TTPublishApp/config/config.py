# -*- coding:utf8 -*-

DEBUG = False

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
]


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'fairy_mirror_db_bz',
        'USER': 'fm_db_bz_pro',
        'PASSWORD': '1biyjegteb274ckmfdy94j6bfz8i6f',
        'HOST': '10.74.22.3',
        'PORT': 3306,
    },
}

# 缓存服务器配置
REDIS_SETTINGS = {
    'host': '10.74.30.12',
    'port': 6379,
    'password': 'crs-cnv36xii:2Xjy26dDXH@R^CRo',
    'db_set': {
        'business': 0,
        'consumer': 1,
        }
}


