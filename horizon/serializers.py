# -*- coding:utf8 -*-
from rest_framework import serializers
from rest_framework import fields as Fields
from django.core.paginator import Paginator
from django.conf import settings
from django.db import models
from horizon.main import timezoneStringTostring
from horizon.models import model_to_dict
from horizon.coss3 import CosS3
from horizon import main

import os
import datetime
import urllib


class BaseListSerializer(serializers.ListSerializer):
    def list_data(self, page_size=settings.PAGE_SIZE, page_index=1, **kwargs):
        """
        函数功能：分页
        返回数据格式为：{'count': 当前返回的数据量,
                       'all_count': 总数据量,
                       'has_next': 是否有下一页,
                       'data': [{
                                  model数据
                                },...]
                       }
        """
        # page size不能超过默认最大值，如果超过，则按page size默认最大值返回数据
        if page_size > settings.MAX_PAGE_SIZE:
            page_size = settings.MAX_PAGE_SIZE
        serializer = self.perfect_result()
        paginator = Paginator(serializer, page_size)

        try:
            page = paginator.page(page_index)
        except Exception as e:
            return {'count': 0,
                    'all_count': len(serializer),
                    'has_next': False,
                    'data': {}}

        has_next = True
        if len(page.object_list) < page_size:
            has_next = False
        elif page_size * page_index >= len(serializer):
            has_next = False
        results = {'count': len(page.object_list),
                   'all_count': len(serializer),
                   'has_next': has_next,
                   'data': page.object_list}
        return results

    def perfect_result(self):
        dict_format = {}
        if hasattr(self, 'initial_data'):
            if len(self.initial_data) > 0:
                dict_format = self.initial_data[0]
        else:
            if len(self.instance) > 0:
                dict_format = model_to_dict(self.instance[0])
        ordered_dict = self.data
        for item in ordered_dict:
            for key in list(item.keys()):
                if key not in dict_format or not item[key]:
                    continue
                if isinstance(dict_format[key], datetime.datetime):
                    item[key] = timezoneStringTostring(item[key])
                if isinstance(dict_format[key], (models.fields.files.ImageFieldFile, models.fields.files.FieldFile)):
                    image_str = urllib.parse.unquote(item[key])
                    if image_str.startswith('http://') or image_str.startswith('https://'):
                        item['%s_url' % key] = image_str
                    else:
                        item['%s_url' % key] = os.path.join(settings.WEB_URL_FIX,
                                                            'static',
                                                            image_str)
                    item.pop(key)
        return ordered_dict


class BaseSerializer(serializers.Serializer):
    @property
    def data(self):
        _data = super(BaseSerializer, self).data
        return perfect_result(self, _data)


class BaseModelSerializer(serializers.ModelSerializer):
    def __init__(self, instance=None, data=None, **kwargs):
        if data:
            # self.make_perfect_initial_data(data)
            super(BaseModelSerializer, self).__init__(data=data, **kwargs)
        else:
            super(BaseModelSerializer, self).__init__(instance, **kwargs)

    def update(self, instance, validated_data):
        self.make_perfect_initial_data(validated_data)
        return super(BaseModelSerializer, self).update(instance, validated_data)

    @property
    def data(self):
        _data = super(BaseModelSerializer, self).data
        return perfect_result(self, _data)

    def save(self, **kwargs):
        self.make_perfect_initial_data(self.validated_data)
        return super(BaseModelSerializer, self).save(**kwargs)

    def make_perfect_initial_data(self, data):
        fields = self.Meta.model._meta.fields
        model_name = self.Meta.model._meta.model_name
        for field in fields:
            field_name = field.name
            if field_name.endswith('_url') and field_name in data:
                fp_file = open(data[field_name], 'rb')
                perfect_file_name = data[field_name].split('static/')[1]
                # 上传照片至腾讯云cos服务
                CosS3().put_object(body=fp_file, file_name=perfect_file_name)
                data[field_name] = perfect_file_name
                fp_file.close()


def perfect_result(self, _data):
    _fields = self.get_fields()
    for key in list(_data.keys()):
        if not _data[key]:
            continue
        if isinstance(_fields[key], Fields.DateTimeField):
            _data[key] = timezoneStringTostring(_data[key])
        if isinstance(_fields[key], (Fields.ImageField, Fields.FileField)):
            image_str = urllib.parse.unquote(_data[key])
            if image_str.startswith('http://') or image_str.startswith('https://'):
                _data['%s_url' % key] = image_str
            else:
                _data['%s_url' % key] = os.path.join(settings.WEB_URL_FIX,
                                                     'static',
                                                     image_str)
            _data.pop(key)
    return _data


