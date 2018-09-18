# -*- coding:utf8 -*-
from __future__ import unicode_literals
import json
import datetime

from FMBusinessApp.config import REDIS_SETTINGS
from horizon import redis
from django.utils.timezone import now

from users.models import BusinessUser, Group


# 过期时间（单位：秒）
EXPIRES_24_HOURS = 24 * 60 * 60
EXPIRES_10_HOURS = 10 * 60 * 60


class UsersAppCache(object):
    def __init__(self):
        pool = redis.ConnectionPool(host=REDIS_SETTINGS['host'],
                                    port=REDIS_SETTINGS['port'],
                                    db=REDIS_SETTINGS['db_set']['business'])
        self.handle = redis.Redis(connection_pool=pool)

    def get_api_id_key(self, api_id):
        return 'api_id:%s' % api_id

    def get_group_name_key(self, group_name):
        return 'group_instance_group_name:%s' % group_name

    def get_user_id_key(self, user_id):
        return 'user_instance_user_id:%s' % user_id

    def set_data_to_cache(self, key, data):
        self.handle.set(key, data)
        self.handle.expire(key, EXPIRES_24_HOURS)

    def get_group_by_group_name(self, group_name):
        key = self.get_group_name_key(group_name)
        group_instance = self.handle.get(key)
        if not group_instance:
            group_instance = Group.filter_details(group_name=group_name)
            if isinstance(group_instance, Exception):
                return group_instance
            self.set_data_to_cache(key, group_instance)
        return group_instance

    def get_user_by_user_id(self, user_id):
        key = self.get_user_id_key(user_id)
        user_instance = self.handle.get(key)
        if not user_instance:
            user_instance = BusinessUser.get_detail(id=user_id)
            if isinstance(user_instance, Exception):
                return user_instance
            self.set_data_to_cache(key, user_instance)
        return user_instance

