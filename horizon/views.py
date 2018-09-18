# -*- coding: utf8 -*-
from rest_framework.views import APIView as _APIView
from rest_framework.settings import APISettings, DEFAULTS, IMPORT_STRINGS
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from horizon.serializers import (BaseSerializer,
                                 BaseListSerializer,
                                 BaseModelSerializer)
from horizon.http import status as fm_status

from django.db import models
import copy


_default = copy.deepcopy(DEFAULTS)
_default.update(**{
    'PAY_CALLBACK_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',),
    'PAY_CALLBACK_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    )})
_import_strings = list(copy.deepcopy(IMPORT_STRINGS))
_import_strings.extend(['PAY_CALLBACK_AUTHENTICATION_CLASSES',
                        'PAY_CALLBACK_PERMISSION_CLASSES'])

api_settings = APISettings(None, _default, _import_strings)


class APIView(_APIView):
    authentication_classes = api_settings.PAY_CALLBACK_AUTHENTICATION_CLASSES
    permission_classes = api_settings.PAY_CALLBACK_PERMISSION_CLASSES


class FMActionAPIView(generics.GenericAPIView):
    """
    自定义GenericsAPIView Action类方法
    """
    post_form_class = None
    post_serializer_class = None
    put_form_class = None
    put_serializer_class = None
    delete_form_class = None
    delete_serializer_class = None
    model_class = None

    def get_instance(self, request, pk):
        kwargs = {'pk': pk}
        return self.model_class.get_object(translate_cos_url=False, **kwargs)

    def is_request_data_valid(self, **kwargs):
        return True, None

    def get_perfect_request_data(self, **kwargs):
        return kwargs

    def post(self, request, *args, **kwargs):
        """
        创建数据
        :param request: 
        :param args: 
        :param kwargs: 
        :return: 
        """
        if not (self.post_form_class or self.post_serializer_class):
            return fm_status.return_error_response(fm_status.HTTP_405_METHOD_NOT_ALLOWED)

        form = self.post_form_class(request.data, request.FILES)
        if not form.is_valid():
            return fm_status.return_error_response(fm_status.HTTP_400_BAD_REQUEST, form.errors)

        cld = form.cleaned_data
        is_valid, error_message = self.is_request_data_valid(**cld)
        if not is_valid:
            return fm_status.return_error_response(fm_status.HTTP_400_BAD_REQUEST, error_message)

        cld = self.get_perfect_request_data(**cld)
        serializer = self.post_serializer_class(data=cld, request=request)
        if not serializer.is_valid():
            return fm_status.return_error_response(fm_status.HTTP_400_BAD_REQUEST, serializer.errors)
        try:
            serializer.save()
        except Exception as e:
            return fm_status.return_error_response(fm_status.HTTP_400_BAD_REQUEST, e.args)
        return fm_status.return_success_response()

    def put(self, request, *args, **kwargs):
        """
        更新数据
        :param request: 
        :param args: 
        :param kwargs: 
        :return: 
        """
        if not (self.put_form_class or self.put_serializer_class):
            return fm_status.return_error_response(fm_status.HTTP_405_METHOD_NOT_ALLOWED)

        form = self.put_form_class(request.data, request.FILES)
        if not form.is_valid():
            return fm_status.return_error_response(fm_status.HTTP_400_BAD_REQUEST, form.errors)

        cld = form.cleaned_data
        is_valid, error_message = self.is_request_data_valid(**cld)
        if not is_valid:
            return fm_status.return_error_response(fm_status.HTTP_400_BAD_REQUEST, error_message)

        instance = self.get_instance(request, cld['pk'])
        if isinstance(instance, Exception):
            return fm_status.return_error_response(fm_status.HTTP_400_BAD_REQUEST, instance.args)

        serializer = self.put_serializer_class(instance)
        try:
            serializer.update(instance, cld)
        except Exception as e:
            return fm_status.return_error_response(fm_status.HTTP_400_BAD_REQUEST, e.args)
        return fm_status.return_success_response()

    def delete(self, request, *args, **kwargs):
        """
        删除数据
        :param request: 
        :param args: 
        :param kwargs: 
        :return: 
        """
        if not (self.delete_form_class or self.delete_serializer_class):
            return fm_status.return_error_response(fm_status.HTTP_405_METHOD_NOT_ALLOWED)

        form = self.delete_form_class(request.data, request.FILES)
        if not form.is_valid():
            return fm_status.return_error_response(fm_status.HTTP_400_BAD_REQUEST, form.errors)

        cld = form.cleaned_data
        instance = self.get_instance(request, cld['pk'])
        if isinstance(instance, Exception):
            return fm_status.return_error_response(fm_status.HTTP_400_BAD_REQUEST, instance.args)

        serializer = self.delete_serializer_class(instance)
        try:
            serializer.delete(instance)
        except Exception as e:
            return fm_status.return_error_response(fm_status.HTTP_400_BAD_REQUEST, e.args)
        return fm_status.return_success_response()


class FMDetailAPIView(generics.GenericAPIView):
    """
    获取详情
    """
    detail_form_class = None
    detail_serializer_class = None
    model_class = None

    def get_instance(self, request, **kwargs):
        return self.model_class.get_object(**kwargs)

    def is_request_data_valid(self, **kwargs):
        return True, None

    def post(self, request, *args, **kwargs):
        """
        获取详情
        """
        form = self.detail_form_class(request.data)
        if not form.is_valid():
            return fm_status.return_error_response(fm_status.HTTP_400_BAD_REQUEST, form.errors)

        cld = form.cleaned_data
        is_valid, error_message = self.is_request_data_valid(**cld)
        if not is_valid:
            return fm_status.return_error_response(fm_status.HTTP_400_BAD_REQUEST, error_message)

        instance = self.get_instance(request, **cld)
        if isinstance(instance, Exception):
            return fm_status.return_error_response(fm_status.HTTP_400_BAD_REQUEST, instance.args)

        if not self.model_class or not isinstance(instance, self.model_class):
            serializer = self.detail_serializer_class(data=instance)
            if not serializer.is_valid():
                return fm_status.return_error_response(fm_status.HTTP_400_BAD_REQUEST, serializer.errors)
        else:
            serializer = self.detail_serializer_class(instance)
        return fm_status.return_success_response(serializer.data)


class FMListAPIView(generics.GenericAPIView):
    """
    获取详情列表
    """
    list_form_class = None
    list_serializer_class = None
    model_class = None

    def get_instances_list(self, request, **kwargs):
        return self.model_class.filter_objects(**kwargs)

    def is_request_data_valid(self, request=None, **kwargs):
        return True, None

    def get_perfect_request_data(self, **kwargs):
        return kwargs

    def post(self, request, *args, **kwargs):
        """
        获取详情列表
        """
        form = self.list_form_class(request.data)
        if not form.is_valid():
            return fm_status.return_error_response(fm_status.HTTP_400_BAD_REQUEST, form.errors)

        cld = form.cleaned_data
        is_valid, error_message = self.is_request_data_valid(request=request, **cld)
        if not is_valid:
            return fm_status.return_error_response(fm_status.HTTP_400_BAD_REQUEST, error_message)

        cld = self.get_perfect_request_data(**cld)
        instances = self.get_instances_list(request, **cld)
        if isinstance(instances, Exception):
            return fm_status.return_error_response(fm_status.HTTP_400_BAD_REQUEST, instances.args)

        if isinstance(self.list_serializer_class.child, BaseModelSerializer):
            serializer = self.list_serializer_class(instances)
        else:
            serializer = self.list_serializer_class(data=instances)
            if not serializer.is_valid():
                return fm_status.return_error_response(fm_status.HTTP_400_BAD_REQUEST, serializer.errors)
        data_list = serializer.list_data(**cld)
        if isinstance(data_list, Exception):
            return fm_status.return_error_response(fm_status.HTTP_400_BAD_REQUEST, data_list.args)
        return fm_status.return_success_response(data=data_list.pop('data'), **data_list)

