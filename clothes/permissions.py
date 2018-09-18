# -*- coding:utf8 -*-
from rest_framework import permissions
from clothes.forms import ClothesUpdateForm, ClothesBatchUpdateForm
from horizon.permission import DjangoAPIPermissionOrAnonReadOnly


class IsOwnerOrReadOnly(permissions.IsAuthenticated):
    """
    自定义权限，只有创建者才能编辑
    """
    common_store_user_fields = ('pk', 'goods_id', 'is_active', 'does_display_wechat')
    store_user_fields = ('pk', 'goods_id', 'present_price', 'is_active',
                         'is_new', 'is_hot_sale', 'is_discount',
                         'does_display_mirror', 'does_display_wechat',
                         'picture_order_list', 'video_order_list')
    brand_user_fields = ('pk', 'title', 'subtitle', 'description', 'goods_id',
                         'original_price', 'present_price', 'recommend_title',
                         'recommend_subtitle', 'gender', 'shape', 'is_active',
                         'is_new', 'is_hot_sale', 'is_discount', 'video',
                         'picture1', 'picture2', 'picture3', 'picture4',
                         'picture_order_list', 'video_order_list', 'tags',
                         'color', 'classify_id', 'does_display_mirror',
                         'does_display_wechat', 'fabric_component', 'stereotype',
                         'thickness', 'elastic')
    root_user_fields = ('pk', 'clothes_color_id', 'clothes_style_id')

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the dishes.
        return obj.user_id == request.user.is_admin

    def has_permission(self, request, view):
        """
        自定义权限
        """
        has_permission = super(IsOwnerOrReadOnly, self).has_permission(request, view)
        if not has_permission:
            return has_permission

        # 数据修改方法权限判断
        if request.method == 'PUT':
            form = ClothesUpdateForm(request.data)
            if not form.is_valid():
                return True

            cld = form.cleaned_data
            # 普通门店：修改权限判断
            if request.user.is_common_store_user:
                for key in cld:
                    if key not in self.common_store_user_fields:
                        return False
            # 高级门店用户：修改权限判断
            elif request.user.is_senior_store_user:
                for key in cld:
                    if key not in self.store_user_fields:
                        return False
            # 品牌用户：修改权限判断
            elif request.user.is_brand_user:
                for key in cld:
                    if key not in self.brand_user_fields:
                        return False
            # root用户：修改权限判断
            elif request.user.is_root_user:
                for key in cld:
                    if key not in self.root_user_fields:
                        return False
            else:
                return False
        # elif request.method == 'DELETE':
        return True


class IsClothesListPermission(permissions.IsAuthenticated):
    """
    自定义权限
    """
    def has_permission(self, request, view):
        """
        自定义权限
        """
        has_permission = super(IsClothesListPermission, self).has_permission(request, view)
        if not has_permission:
            return has_permission

        # 获取服装列表权限判断
        # root用户：必须选择品牌
        if request.user.is_root_user:
            if 'business_user_id' not in request.data:
                return False
        return True


class IsClothesBatchActionPermission(DjangoAPIPermissionOrAnonReadOnly):
    """
    自定义权限
    """
    common_store_user_action_field_values = ('active', 'inactive')
    store_user_action_field_values = ('active', 'inactive', 'hot_sale', 'not_hot_sale',
                                      'new', 'not_new', 'discount', 'not_discount')
    brand_action_field_values = ('active', 'inactive', 'hot_sale', 'not_hot_sale',
                                 'new', 'not_new', 'discount', 'not_discount')

    def has_permission(self, request, view):
        """
        自定义权限，品牌权限有：上下架、新品、取消新品、热销、取消热销、促销、取消促销
                  高级门店权限有：上下架、新品、取消新品、热销、取消热销、促销、取消促销
                  普通门店权限有：上下架
        """
        has_permission = super(IsClothesBatchActionPermission, self).has_permission(request, view)
        if not has_permission:
            return has_permission

        # 数据修改方法权限判断
        if request.method == 'PUT':
            form = ClothesBatchUpdateForm(request.data)
            if not form.is_valid():
                return True

            cld = form.cleaned_data
            # 普通门店：批量修改数据权限判断
            if request.user.is_common_store_user:
                if cld['action'] not in self.common_store_user_action_field_values:
                    return False
            # 高级门店用户：批量修改数据权限判断
            elif request.user.is_senior_store_user:
                if cld['action'] not in self.store_user_action_field_values:
                    return False
            # 品牌用户：批量修改数据权限判断
            elif request.user.is_brand_user:
                if cld['action'] not in self.brand_action_field_values:
                    return False
            else:
                return False
        return True
