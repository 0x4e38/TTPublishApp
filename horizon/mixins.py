# -*- coding:utf8 -*-
from horizon.models import model_to_dict, get_perfect_filter_params
from horizon.coss3 import CosS3
from django.conf import settings


class BaseModelMixin(object):
    """
    数据库操作混合类
    """
    @property
    def perfect_detail(self):
        return model_to_dict(self)

    @classmethod
    def get_object(cls, *args, translate_cos_url=True, **kwargs):
        kwargs = get_perfect_filter_params(cls, **kwargs)
        try:
            instance = cls.objects.get(*args, **kwargs)
        except Exception as e:
            return e

        # 转换图片、文件的访问地址为腾讯云cos服务的有效地址
        if translate_cos_url:
            for field in instance._meta.fields:
                key_name = field.name
                if key_name.endswith('_url'):
                    access_url = CosS3().get_presigned_download_url(getattr(instance, key_name))
                    setattr(instance, key_name, access_url)
        return instance

    @classmethod
    def get_detail(cls, *args, **kwargs):
        kwargs = get_perfect_filter_params(cls, **kwargs)
        instance = cls.get_object(*args, **kwargs)
        if isinstance(instance, Exception):
            return instance
        return instance.perfect_detail

    @classmethod
    def filter_objects(cls, *args, translate_cos_url=True, **kwargs):
        page_size = kwargs.get('page_size', settings.MAX_PAGE_SIZE)
        page_index = kwargs.get('page_index', 1)
        offset = page_size * (page_index - 1)
        limit = page_size

        kwargs = get_perfect_filter_params(cls, **kwargs)
        try:
            instances = cls.objects.filter(*args, **kwargs)[offset: limit]
        except Exception as e:
            return e

        # 转换图片、文件的访问地址为腾讯云cos服务的有效地址
        if translate_cos_url:
            for instance in instances:
                for field in instance._meta.fields:
                    key_name = field.name
                    if key_name.endswith('_url'):
                        access_url = CosS3().get_presigned_download_url(getattr(instance, key_name))
                        setattr(instance, key_name, access_url)
        return instances

    @classmethod
    def filter_details(cls, *args, **kwargs):
        # kwargs = get_perfect_filter_params(cls, **kwargs)
        instances = cls.filter_objects(*args, **kwargs)
        if isinstance(instances, Exception):
            return instances
        details = [ins.perfect_detail for ins in instances]
        return details

