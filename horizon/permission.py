# -*- coding:utf8 -*-
from rest_framework import permissions


class DjangoAPIPermissionOrAnonReadOnly(permissions.IsAuthenticated):
    """
    自定义权限，只能访问该用户能访问的api
    """
    def has_object_permission(self, request, view, obj):
        return super(DjangoAPIPermissionOrAnonReadOnly, self).has_object_permission(request, view, obj)

    def has_permission(self, request, view):
        """
        自定义权限：检查request用户是否有权限访问该接口
        :param request: 访问请求
        :param view: 访问的视图
        :return: True or False
        """
        has_permission = super(DjangoAPIPermissionOrAnonReadOnly, self).has_permission(request, view)
        if not has_permission:
            return has_permission

        # 查找request用户是否有权限访问该接口
        # 获取当前调用请求的api
        call_api = '%s:%s' % (request.path, request.method.upper())
        if not request.user.has_permission_call_api(call_api):
            return False
        return True
