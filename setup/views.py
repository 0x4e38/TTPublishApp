# -*- coding: utf8 -*-
from rest_framework import viewsets
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status

from setup.serializers import (AndroidApkVersionRecordSerializer,
                               AndroidApkVersionRecordListSerializer)
from setup.forms import (ApkUploadForm,
                         ApkUpdateStatusForm,
                         ApkVersionListForm)
from Consumer_App.cs_setup.models import AndroidApkVersionRecord

from horizon.views import APIView
from horizon.http import status as fm_status
from horizon.main import make_random_number_of_string
from horizon import main
import copy
import urllib
import random
import json


class ApkUploadAction(APIView):
    """
    android APK上传操作
    """
    def get_instance(self, request, pk):
        return AndroidApkVersionRecord.get_object(**{'pk': pk})

    def post(self, request, *args, **kwargs):
        """
        上传android apk文件
        :param request: 
        :param args: 
        :param kwargs: 
        :return: 
        """
        form = ApkUploadForm(request.data, request.FILES)
        if not form.is_valid():
            return fm_status.return_error_response(fm_status.HTTP_400_BAD_REQUEST, form.errors)

        cld = form.cleaned_data
        serializer = AndroidApkVersionRecordSerializer(data=cld)
        if not serializer.is_valid():
            return fm_status.return_error_response(fm_status.HTTP_400_BAD_REQUEST, serializer.errors)
        try:
            serializer.save()
        except Exception as e:
            return fm_status.return_error_response(fm_status.HTTP_400_BAD_REQUEST, e.args)
        return fm_status.return_success_response()

    def put(self, request, *args, **kwargs):
        """
        修改发布状态
        :param request: 
        :param args: 
        :param kwargs: 
        :return: 
        """
        form = ApkUpdateStatusForm(request.data)
        if not form.is_valid():
            return fm_status.return_error_response(fm_status.HTTP_400_BAD_REQUEST, form.errors)

        cld = form.cleaned_data
        instance = self.get_instance(request, cld['pk'])
        if isinstance(instance, Exception):
            return fm_status.return_error_response(fm_status.HTTP_400_BAD_REQUEST, instance.args)

        serializer = AndroidApkVersionRecordSerializer(instance)
        try:
            serializer.update_status(instance, cld['status'])
        except Exception as e:
            return fm_status.return_error_response(fm_status.HTTP_400_BAD_REQUEST, e.args)
        return fm_status.return_success_response()


class ApkVersionList(APIView):
    """
    android APK包列表
    """
    def get_details(self, request):
        return AndroidApkVersionRecord.filter_details()

    def post(self, request, *args, **kwargs):
        """
        获取android apk包列表
        :param request: 
        :param args: 
        :param kwargs: 
        :return: 
        """
        form = ApkVersionListForm(request.data)
        if not form.is_valid():
            return fm_status.return_error_response(fm_status.HTTP_400_BAD_REQUEST, form.errors)

        cld = form.cleaned_data
        details = self.get_details(request)
        serializer = AndroidApkVersionRecordListSerializer(data=details)
        if not serializer.is_valid():
            return fm_status.return_error_response(fm_status.HTTP_400_BAD_REQUEST, serializer.errors)
        data_list = serializer.list_data(**cld)
        if isinstance(data_list, Exception):
            return fm_status.return_error_response(fm_status.HTTP_400_BAD_REQUEST, data_list.args)
        return fm_status.return_success_response(data_list)


class ApkVersionDetail(APIView):
    """
    拉取apk发布版本
    """
    def get_release_instance(self):
        return AndroidApkVersionRecord.get_object(**{'status': 1})

    def post(self, request, *args, **kwargs):
        """
        获取android apk包列表
        :param request: 
        :param args: 
        :param kwargs: 
        :return: 
        """
        instance = self.get_release_instance()
        if isinstance(instance, Exception):
            return fm_status.return_error_response(fm_status.HTTP_400_BAD_REQUEST, instance.args)
        serializer = AndroidApkVersionRecordSerializer(instance)
        return fm_status.return_success_response(serializer.data)
