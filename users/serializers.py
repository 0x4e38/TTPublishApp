# -*- coding:utf8 -*-
from django.contrib.auth.models import User, Group
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from django.conf import settings

from horizon.models import model_to_dict
from horizon import main
from horizon.decorators import has_permission_to_update
from horizon.serializers import (BaseListSerializer,
                                 BaseModelSerializer,
                                 BaseSerializer,
                                 timezoneStringTostring)
from users.models import (BusinessUser,
                          IdentifyingCode,
                          BatchUploadStoreFileTemplate,
                          AreaCity,
                          AreaProvince,
                          BusinessUserAction)

import urllib
import os
import json
import re
import copy


class UserSerializer(BaseModelSerializer):
    request = None

    def __init__(self, instance=None, data=None, request=None, **kwargs):
        if data:
            self.request = request
            data['brand'] = request.user.brand
            data['password'] = make_password(main.make_random_char_and_number_of_string())
            super(UserSerializer, self).__init__(data=data, **kwargs)
        else:
            super(UserSerializer, self).__init__(instance, **kwargs)

    class Meta:
        model = BusinessUser
        fields = '__all__'

    def save(self, **kwargs):
        return BusinessUserAction().create(self.request, self.validated_data)

    @has_permission_to_update
    def update_password(self, request, instance, validated_data):
        password = validated_data.get('password', None)
        if password is None:
            raise ValueError('Password is cannot be empty.')
        validated_data['password'] = make_password(password)
        return super(UserSerializer, self).update(instance, validated_data)

    @has_permission_to_update
    def update_userinfo(self, request, instance, validated_data):
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        return super(UserSerializer, self).update(instance, validated_data)

    def binding_phone_to_user(self, request, instance, validated_data):
        _validated_data = {'phone': validated_data['username']}
        instance = super(UserSerializer, self).update(instance, _validated_data)
        return instance


class UserInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessUser
        fields = ('id', 'phone', 'nickname', 'head_picture',)


class BrandDetailSerializer(BaseSerializer):
    id = serializers.IntegerField()
    phone = serializers.CharField()
    brand = serializers.CharField()
    manager = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    role = serializers.IntegerField()


class BrandListSerializer(BaseListSerializer):
    child = BrandDetailSerializer()


class UserDetailSerializer(BaseSerializer):
    phone = serializers.CharField()
    business_name = serializers.CharField(allow_blank=True, allow_null=True)
    brand = serializers.CharField()
    manager = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    address = serializers.CharField(allow_blank=True, allow_null=True)
    hotline = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    logo_url = serializers.CharField(allow_null=True, allow_blank=True)
    longitude = serializers.CharField(allow_blank=True, allow_null=True)
    latitude = serializers.CharField(allow_blank=True, allow_null=True)
    permission_group = serializers.CharField()
    role = serializers.IntegerField()


class UserListSerializer(BaseListSerializer):
    child = UserDetailSerializer()


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')


class IdentifyingCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = IdentifyingCode
        fields = '__all__'


class BatchUploadStoreFileTemplateSerializer(BaseModelSerializer):
    class Meta:
        model = BatchUploadStoreFileTemplate
        fields = '__all__'


class StoreDetailSerializer(BaseSerializer):
    id = serializers.IntegerField()
    brand = serializers.CharField()
    phone = serializers.CharField()
    business_name = serializers.CharField(allow_null=True, allow_blank=True)
    permission_group = serializers.CharField()
    province = serializers.CharField()
    province_id = serializers.IntegerField()
    city_id = serializers.IntegerField()
    city = serializers.CharField()
    address = serializers.CharField()
    manager = serializers.CharField(allow_null=True, allow_blank=True)
    email = serializers.EmailField(allow_null=True, allow_blank=True)
    backup_phone = serializers.CharField()
    hotline = serializers.CharField()


class StoreListSerializer(BaseListSerializer):
    child = StoreDetailSerializer()


class AreaProvinceSerializer(BaseModelSerializer):
    class Meta:
        model = AreaProvince
        fields = ('id', 'province')


class AreaProvinceListSerializer(BaseListSerializer):
    child = AreaProvinceSerializer()


class AreaCitySerializer(BaseModelSerializer):
    class Meta:
        model = AreaCity
        fields = ('id', 'province_id', 'city')


class AreaCityListSerializer(BaseListSerializer):
    child = AreaCitySerializer()
