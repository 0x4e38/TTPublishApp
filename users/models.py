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

    @property
    def perfect_detail(self):
        update_dict = {'province': None,
                       'city': None,
                       'permission_group': None}

        detail = super(BusinessUser, self).perfect_detail
        city_instance = AreaCity.get_object(id=detail['city_id'])
        if not isinstance(city_instance, Exception):
            province_ins = AreaProvince.get_object(id=city_instance.province_id)
            update_dict['province'] = province_ins.province
            update_dict['province_id'] = province_ins.id
            update_dict['city'] = city_instance.city

        permission_group_detail = Group.get_detail(id=detail['permission_group_id'])
        if not isinstance(permission_group_detail, Exception):
            update_dict['permission_group'] = permission_group_detail['group_name']
            update_dict['api_list'] = permission_group_detail['api_list']
        detail.update(**update_dict)

        if detail['email'] is None:
            detail['email'] = ''
        return detail

    def has_permission_call_api(self, api):
        """
        是否有访问api的权限
        :return: 
        """
        if api in self.perfect_detail['api_list']:
            return True
        return False

    @classmethod
    def get_user_detail(cls, request):
        """
        return: ConsumerUser instance
        """
        try:
            return cls.objects.get(pk=request.user.id)
        except Exception as e:
            return e

    @classmethod
    def filter_details(cls, *args, fuzzy=True, **kwargs):
        if fuzzy:
            for key in list(kwargs.keys()):
                if key in cls.FMMeta.fuzzy_fields:
                    kwargs['%s__contains' % key] = kwargs[key]
                    kwargs.pop(key)

        return super(BusinessUser, cls).filter_details(*args, **kwargs)

    @classmethod
    def get_objects_list(cls, request, **kwargs):
        """
        获取用户列表
        权限控制：只有管理员可以访问这些数据
        """
        if not request.user.is_admin:
            return Exception('Permission denied, Cannot access the method')

        _kwargs = {}
        if 'start_created' in kwargs:
            _kwargs['created__gte'] = kwargs['start_created']
        if 'end_created' in kwargs:
            _kwargs['created__lte'] = kwargs['end_created']
        _kwargs['is_admin'] = False
        try:
            return cls.objects.filter(**_kwargs)
        except Exception as e:
            return e

    @classmethod
    def batch_create_store_user(cls, request, business_user_details):
        """
        批量创建门店用户
        :param request: http请求request
        :param business_user_details: 门店用户信息
        :return: 
        """
        instances = []
        # 添加事务
        try:
            with transaction.atomic():
                instances = BusinessUserAction().bulk_create(request, business_user_details)
        except Exception as e:
            return False, e.args
        return True, instances


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


class BusinessUserAction(object):
    """
    创建门店用户 - create, bulk_create
    """
    def get_perfect_init_data(self, request, user_detail):
        """
        :param request: http请求request
        :param user_detail: 门店用户信息
        :return: 
        """
        init_data = {'phone': user_detail['phone'],
                     'city_id': user_detail['city_id'],
                     'address': user_detail['address'],
                     'brand': user_detail['brand'],
                     'permission_group_id': user_detail['permission_group_id'],
                     'business_name': user_detail['business_name'],
                     'manager': user_detail['manager'],
                     'email': user_detail.get('email', None),
                     'backup_phone': user_detail['backup_phone'],
                     'hotline': user_detail['hotline'],
                     # 'role': user_detail['role'],
                     }
        return init_data

    def bulk_create(self, request, business_user_details):
        """
        批量创建
        :param request: request请求
        :param business_user_details: 
        :return: 
        """
        queryset_list = []
        instances = []
        for user_detail in business_user_details:
            init_data = self.get_perfect_init_data(request, user_detail)
            # 没有用bulk_create，bulk_create函数返回初始化的model objs空对象
            instance = BusinessUser(**init_data)
            instance.save()
            instances.append(instance)
            # queryset_list.append(instance)
        # business_user_instances = BusinessUser.objects.bulk_create(queryset_list)
        self.bulk_create_business_user_bind(request, instances)
        return instances

    def create(self, request, business_user_detail):
        """
        创建
        :param request: request请求
        :param business_user_detail: 门店用户信息
        :return: 
        """
        init_data = self.get_perfect_init_data(request, business_user_detail)
        ins = BusinessUser(**init_data)
        ins.save()
        return self.create_business_user_bind(request, ins)

    def bulk_create_business_user_bind(self, request, business_user_instances):
        """
        批量创建品牌和门店所属关系的信息
        :param request: request请求
        :param business_user_instances: 门店用户model对象列表
        :return: 
        """
        init_data_list = []
        for ins in business_user_instances:
            init_data = {'brand_user_id': request.user.id,
                         'business_user_id': ins.id}
            init_data_list.append(BusinessUserBind(**init_data))
        return BusinessUserBind.objects.bulk_create(init_data_list)

    def create_business_user_bind(self, request, business_user_instance):
        """
        创建品牌和门店所属关系的信息
        :param request: request请求
        :param business_user_instance: 门店用户model对象
        :return: 
        """
        init_data = {'brand_user_id': request.user.id,
                     'business_user_id': business_user_instance.id}
        ins = BusinessUserBind(**init_data)
        return ins.save()


class IdentifyingCode(BaseModelMixin, models.Model):
    phone = models.CharField(u'手机号', max_length=20, db_index=True)
    identifying_code = models.CharField(u'验证码', max_length=6)
    expires = models.DateTimeField(u'过期时间', default=minutes_5_plus)

    objects = BaseExpiresManager()

    class Meta:
        db_table = 'fm_identifying_code'
        ordering = ['-expires']

    def __unicode__(self):
        return self.phone


class BusinessUserBind(BaseModelMixin, models.Model):
    """
    品牌和门店的所属关系
    """
    brand_user_id = models.IntegerField(u'品牌用户ID', db_index=True)
    business_user_id = models.IntegerField(u'门店用户ID', unique=True)

    # 数据状态 1：正常 非1：已删除
    status = models.IntegerField(u'数据状态', default=1)
    created = models.DateTimeField(u'创建时间', default=now)
    updated = models.DateTimeField(u'更新时间', auto_now=True)

    objects = BaseManager()

    class Meta:
        db_table = 'fm_business_user_bind'
        ordering = ['-created']

    def __unicode__(self):
        return '%s:%s' % (self.brand_user_id, self.business_user_id)

    @property
    def perfect_detail(self):
        return BusinessUser.get_detail(id=self.business_user_id)


class AreaProvince(BaseModelMixin, models.Model):
    """
    地区-省、直辖市
    """
    province = models.CharField(u'省份名称', max_length=64)
    created = models.DateTimeField(u'创建时间', default=now)
    updated = models.DateTimeField(u'更新时间', auto_now=True)

    class Meta:
        db_table = 'fm_area_province'
        ordering = ['-created']

    def __unicode__(self):
        return '%s' % self.province


class AreaCity(BaseModelMixin, models.Model):
    """
    地区-市
    """
    province_id = models.IntegerField(u'所属省份ID', db_index=True)
    city = models.CharField(u'城市名称', max_length=64)
    # 数据状态 1：正常 非1：已删除
    status = models.IntegerField(u'数据状态', default=1)
    created = models.DateTimeField(u'创建时间', default=now)
    updated = models.DateTimeField(u'更新时间', auto_now=True)

    objects = BaseManager()

    class Meta:
        db_table = 'fm_area_city'
        ordering = ['-created']

    def __unicode__(self):
        return '%s' % self.city


class API(BaseModelMixin, models.Model):
    """
    接口详情
    """
    api = models.CharField(u'api名称', max_length=256)
    # api的http调用方法：如：post, get, put, delete等
    method = models.CharField(u'api的http调用方法', max_length=32)

    # 数据状态 1：正常 非1：已删除
    status = models.IntegerField(u'数据状态', default=1)
    created = models.DateTimeField(u'创建时间', default=now)
    updated = models.DateTimeField(u'更新时间', auto_now=True)

    objects = BaseManager()

    class Meta:
        db_table = 'fm_api_detail'
        ordering = ['-created']

    def __unicode__(self):
        return '%s' % self.api


class GroupPermission(BaseModelMixin, models.Model):
    """
    组权限
    """
    group_id = models.IntegerField(u'权限组ID', db_index=True)
    api_id = models.IntegerField(u'api ID')

    # 数据状态 1：正常 非1：已删除
    status = models.IntegerField(u'数据状态', default=1)
    created = models.DateTimeField(u'创建时间', default=now)
    updated = models.DateTimeField(u'更新时间', auto_now=True)

    objects = BaseManager()

    class Meta:
        db_table = 'fm_group_permission'
        ordering = ['-created']

    def __unicode__(self):
        return '%s:%s' % (self.group_id, self.api_id)


class Group(BaseModelMixin, models.Model):
    """
    权限组
    """
    # 权限组名称：如：1：root（超级管理员）  2：brand（品牌）  3：store_senior（门店：高级权限） 4： store_common (门店：普通权限)
    group_name = models.CharField(u'组名称', max_length=128)

    # 数据状态 1：正常 非1：已删除
    status = models.IntegerField(u'数据状态', default=1)
    created = models.DateTimeField(u'创建时间', default=now)
    updated = models.DateTimeField(u'更新时间', auto_now=True)

    objects = BaseManager()

    class Meta:
        db_table = 'fm_group'
        ordering = ['-created']

    def __unicode__(self):
        return '%s' % self.group_name

    @property
    def perfect_detail(self):
        detail = super(Group, self).perfect_detail
        group_permission_instances = GroupPermission.filter_objects(group_id=self.id)
        api_ids = [ins.api_id for ins in group_permission_instances]
        api_instances = API.filter_objects(**{'id__in': api_ids})
        detail['api_list'] = ['%s:%s' % (ins.api, ins.method.upper()) for ins in api_instances]
        return detail


class BatchUploadStoreFileTemplate(BaseModelMixin, models.Model):
    """
    批量上传门店信息文件模板
    """
    file_url = models.CharField('文件访问路径', max_length=200)
    format = models.CharField('模板格式', max_length=20, default='csv')

    # 数据状态 1： 正常 非1：已删除
    status = models.IntegerField('数据状态', default=1)
    created = models.DateTimeField('创建时间', default=now)
    updated = models.DateTimeField('更新时间', auto_now=True)

    objects = BaseManager()

    class Meta:
        db_table = 'fm_batch_upload_store_file_template'

    def __unicode__(self):
        return self.file_url
