# -*- coding:utf8 -*-
from django.db import models, transaction
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.utils.timezone import now
from django.contrib.auth.hashers import make_password
from oauth2_provider.models import AccessToken

from horizon.models import model_to_dict, BaseExpiresManager, BaseManager
from horizon.main import minutes_15_plus, minutes_5_plus
from horizon.mixins import BaseModelMixin

import datetime
import re
import os


class BusinessUserManager(BaseUserManager):
    def create_user(self, username, password, **kwargs):
        """
        创建商户用户，
        参数包括：username （手机号）
                 password （长度必须不小于6位）
        """
        if not username:
            raise ValueError('Username cannot be null!')
        if len(password) < 6:
            raise ValueError('Password length must not less then 6!')

        user = self.model(phone=username)
        user.set_password(password)
        user.save(using=self._db)
        return user


class BusinessUser(BaseModelMixin, AbstractBaseUser):
    email = models.EmailField(u'email地址', max_length=255, unique=True, null=True)
    phone = models.CharField(u'手机号', max_length=20, unique=True)
    business_name = models.CharField(u'商户名称', max_length=100, default='')
    brand = models.CharField(u'所属品牌', max_length=60, null=True, default='')
    manager = models.CharField(u'经理人姓名', max_length=20, null=True, default='')
    mall_id = models.IntegerField(u'购物中心ID', null=True)
    backup_phone = models.CharField(u'备用手机号', max_length=20, null=True, default='')

    logo_url = models.CharField(u'头像', max_length=200, default='')
    longitude = models.CharField(u'经度', max_length=32, null=True, default='')
    latitude = models.CharField(u'维度', max_length=32, null=True, default='')
    city_id = models.IntegerField(u'地区-市ID', null=True)
    address = models.CharField(u'街道地址', max_length=128, null=True, default='')
    hotline = models.CharField(u'店铺联系电话', max_length=16, null=True)

    # 用户角色 1：root用户 2：品牌用户  3：门店用户
    role = models.IntegerField(u'角色', default=3)
    permission_group_id = models.IntegerField(u'所属权限组ID')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    date_joined = models.DateTimeField(u'创建时间', default=now)
    last_login = models.DateTimeField(u'最后登录时间', auto_now=True)

    objects = BusinessUserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['business_name']

    class Meta:
        db_table = 'fm_auth_user'
        # unique_together = ('nickname', 'food_court_id')

    class FMMeta:
        fuzzy_fields = ('business_name', )

    def __unicode__(self):
        return self.phone

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    @property
    def is_common_store_user(self):
        if self.role == 3 and self.perfect_detail['permission_group'] == 'store_common':
            return True
        return False

    @property
    def is_senior_store_user(self):
        if self.role == 3 and self.perfect_detail['permission_group'] == 'store_senior':
            return True
        return False

    @property
    def is_store_user(self):
        if self.role == 3:
            return True
        return False

    @property
    def is_root_user(self):
        if self.role == 1:
            return True
        return False

    @property
    def is_brand_user(self):
        if self.role == 2:
            return True
        return False


def make_token_expire(request):
    """
    置token过期
    """
    header = request.META
    token = header['HTTP_AUTHORIZATION'].split()[1]
    try:
        _instance = AccessToken.objects.get(token=token)
        _instance.expires = now()
        _instance.save()
    except:
        pass
    return True

