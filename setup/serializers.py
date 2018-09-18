# -*- coding:utf8 -*-
from rest_framework import serializers
from django.conf import settings

from horizon.models import model_to_dict
from horizon import main
from horizon.serializers import (BaseListSerializer,
                                 BaseModelSerializer,
                                 BaseSerializer)
from Consumer_App.cs_setup.models import AndroidApkVersionRecord

import hashlib
import sys
import os
import stat


class AndroidApkVersionRecordSerializer(BaseModelSerializer):
    def __init__(self, instance=None, data=None, **kwargs):
        if data:
            super(AndroidApkVersionRecordSerializer, self).__init__(data=data, **kwargs)
        else:
            super(AndroidApkVersionRecordSerializer, self).__init__(instance, **kwargs)

    class Meta:
        model = AndroidApkVersionRecord
        fields = '__all__'

    def save(self, **kwargs):
        instance = super(AndroidApkVersionRecordSerializer, self).save(**kwargs)
        file_name = os.path.join(settings.MEDIA_ROOT, instance.apk_file.name)
        md5_ins = hashlib.md5()
        with open(file_name, 'rb') as fp:
            for line in fp:
                md5_ins.update(line)

        instance.md5 = md5_ins.hexdigest().lower()
        instance.save()

        # 修改文件权限，标记所有用户可读
        fname = os.path.join(settings.MEDIA_ROOT, instance.apk_file.name)
        os.chmod(fname, (stat.S_IREAD + stat.S_IRGRP + stat.S_IROTH))     # read by owner, group, other

    def update_status(self, instance, status):
        validated_data = {'status': status}
        # 下线状态
        if status == 2:
            return super(AndroidApkVersionRecordSerializer, self).update(instance, validated_data)
        # 发布状态
        else:
            _kwargs = {'status': 1}
            AndroidApkVersionRecord.make_instances_status_to_canceled(**_kwargs)
            return super(AndroidApkVersionRecordSerializer, self).update(instance, validated_data)


class AndroidApkVersionDetailSerializer(BaseSerializer):
    id = serializers.IntegerField()
    version = serializers.CharField()
    apk_file = serializers.FileField()
    apk_file_name = serializers.CharField()
    md5 = serializers.CharField()
    status = serializers.IntegerField()

    created = serializers.DateTimeField()
    updated = serializers.DateTimeField()


class AndroidApkVersionRecordListSerializer(BaseListSerializer):
    child = AndroidApkVersionDetailSerializer()

