# -*- coding:utf8 -*-
from rest_framework import serializers
from django.conf import settings

from horizon.models import model_to_dict
from horizon import main
from horizon.serializers import (BaseListSerializer,
                                 BaseModelSerializer,
                                 BaseSerializer,
                                 timezoneStringTostring)
from clothes.models import Clothes
from horizon.main import BaseImage

import urllib
import os
import json
import re
import copy


class BusinessStatisticalSerializer(BaseSerializer):
    mirror_used_count = serializers.IntegerField()    # 试衣镜使用人数
    try_on_count = serializers.IntegerField()         # 试穿人数
    per_used_seconds = serializers.IntegerField()     # 人均使用时长
    per_try_on_count = serializers.FloatField()       # 人均试穿件数


class ClothesTryOnNumberSerializer(BaseSerializer):
    date = serializers.CharField()
    count = serializers.IntegerField()


class ClothesTryOnNumberListSerializer(BaseListSerializer):
    child = ClothesTryOnNumberSerializer()

