# -*- coding: utf8 -*-
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import now

from business.serializers import (BusinessStatisticalSerializer,
                                  ClothesTryOnNumberSerializer,
                                  ClothesTryOnNumberListSerializer)
from business.forms import (ClothesTryOnNumberForm,
                            BusinessStatisticalForm)
from Consumer_App.cs_recommend.models import TryOnClothesRecord
from Consumer_App.cs_images.models import ConsumerBodyImage
from Admin_App.ad_devices.models import DeviceManage, Device
from horizon.views import (FMActionAPIView,
                           FMDetailAPIView,
                           FMListAPIView)
from horizon.http import status as fm_status
from horizon import main

import json
import random


class BusinessStatisticalDetail(FMDetailAPIView):
    """
    获取镜子使用人数等统计数字
    """
    detail_form_class = BusinessStatisticalForm
    detail_serializer_class = BusinessStatisticalSerializer
    model_class = None

    def get_instance(self, request, **kwargs):
        manage_instances = DeviceManage.filter_objects(**{'business_user_id': request.user.id})
        device_instances = Device.filter_objects(**{'asset_id__in': [ins.asset_id for ins in manage_instances]})
        device_ids = [ins.device_id for ins in device_instances]

        mirror_used_count = ConsumerBodyImage.get_used_count_for_business(device_ids)
        try_on_count, per_try_on_count = TryOnClothesRecord.get_try_on_numbers_for_business(device_ids)

        return_data = {'mirror_used_count': mirror_used_count,
                       'try_on_count': try_on_count,
                       'per_used_seconds': random.choice([10, 20, 30, 40, 50]),
                       'per_try_on_count': per_try_on_count}
        return return_data

    def post(self, request, *args, **kwargs):
        """
        获取镜子使用情况的统计信息
        :param request: 
        :param args: 
        :param kwargs: 
        :return: 
        """
        return super(BusinessStatisticalDetail, self).post(request, *args, **kwargs)


class ClothesTryOnNumberList(FMListAPIView):
    """
    每日试穿人数列表
    """
    list_form_class = ClothesTryOnNumberForm
    list_serializer_class = ClothesTryOnNumberListSerializer
    model_class = None

    def get_instances_list(self, request, **kwargs):
        manage_instances = DeviceManage.filter_objects(**{'business_user_id': request.user.id})
        device_instances = Device.filter_objects(**{'asset_id__in': [ins.asset_id for ins in manage_instances]})
        device_ids = [ins.device_id for ins in device_instances]

        time_line_list = TryOnClothesRecord.get_try_on_count_for_time_line(
            device_ids,
            start_date=main.make_time_delta(days=-15),
            end_date=now()
        )

        # date_count_list = []
        # random_list = [i for i in (25, 100)]
        #
        # for delta in range(-14, 1):
        #     date_time = main.make_time_delta(days=delta)
        #     day = date_time.day
        #     month = date_time.month
        #     date_count_list.append({'date': '%02d/%2d' % (month, day),
        #                             'count': random.choice(random_list)})

        return time_line_list

    def post(self, request, *args, **kwargs):
        """
        获取每日试穿人数列表
        :param request: 
        :param args: 
        :param kwargs: 
        :return: 
        """
        return super(ClothesTryOnNumberList, self).post(request, *args, **kwargs)


