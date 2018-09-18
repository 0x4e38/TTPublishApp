# -*- coding:utf8 -*-
from rest_framework import serializers
from django.conf import settings

from horizon.models import model_to_dict
from horizon import main
from horizon.serializers import (BaseListSerializer,
                                 BaseModelSerializer,
                                 BaseSerializer,
                                 timezoneStringTostring)
from clothes.models import (Clothes,
                            AdvertisingCopy,
                            ClothesMiddleClassify,
                            ClothesLargeClassify,
                            BatchUploadFileTemplate,
                            ExportFileRecord,
                            StoresClothes,
                            ClothesColor,
                            ClothesStyle,
                            StoreClothesAction)
from Admin_App.ad_stores.models import Store
from horizon.main import BaseImage
from horizon import main

import urllib
import os
import json
import re
import copy
import decimal


class ClothesSerializer(BaseModelSerializer):
    picture_postfix_list = ('PNG', 'JPG', 'JPEG')
    video_postfix_list = ('MP4', 'FLV', 'RMVB', '3GP', 'AVI', 'MKV',
                          'WMV', 'MPG', 'VOB', 'SWF', 'MOV')
    picture_list = ('picture1', 'picture2', 'picture3', 'picture4')
    video_list = ('video', )
    picture_url_list = ('picture1_url', 'picture2_url', 'picture3_url', 'picture4_url')
    video_url_list = ('video_url', )
    picture_order_list = ['picture1', 'picture2', 'picture3', 'picture4']
    video_max_size = 4 * 1024 * 1024
    picture_max_size = 2 * 1024 * 1024
    original_picture_max_size = settings.FILE_UPLOAD_MAX_MEMORY_SIZE
    height_width_ratio = 4 / 3
    max_height = 4000
    max_width = 3000
    _p_errors = None

    def __init__(self, instance=None, data=None, request=None, **kwargs):
        if data:
            if request:
                data['business_user_id'] = request.user.id

            if 'present_price' not in data:
                data['present_price'] = data['original_price']
            if data['present_price'] > data['original_price']:
                self._p_errors = 'present_price can not greater than original_price!'
            elif data['present_price'] < data['original_price']:
                data['is_discount'] = 1

            # "上下架状态"和"是否在小程序端展示"联动
            is_active = does_display_wechat = data.get('is_active', -1)
            if is_active != -1:
                data['is_active'] = is_active
                data['does_display_wechat'] = does_display_wechat

            # 生成main_sku_code
            classify_ins = ClothesMiddleClassify.get_object(pk=data['classify_id'])
            # store_ins = Store.get_object(business_user_id=request.user.id)
            data['main_sku_code'] = '%02d%02d%06d%s' % (classify_ins.large_classify_id,
                                                        classify_ins.id,
                                                        request.user.id,
                                                        # store_ins.id,
                                                        main.make_random_char_and_number_of_string(4))
            picture_index = 0
            video_index = 0
            for file_key in self.picture_list + self.video_list:
                if data.get(file_key):
                    perfect_file_key = '%s_url' % file_key
                    data[perfect_file_key] = data.pop(file_key)
                    if perfect_file_key == 'video_url':
                        if data[perfect_file_key].name.upper().split('.')[-1] in self.video_postfix_list:
                            if data[perfect_file_key].size > self.video_max_size:
                                self._p_errors = 'Video file size is too large!'
                            else:
                                data[perfect_file_key] = BaseImage.save_file_to_disk_for_in_memory_uploaded_file(
                                    data[perfect_file_key]
                                )
                            video_index += 1
                        else:
                            self._p_errors = 'Video file format is incorrect!'
                    else:
                        if data[perfect_file_key].name.upper().split('.')[-1] in self.picture_postfix_list:
                            # 判断图片源文件大小是否超过规定的上限
                            if data[perfect_file_key].size > self.original_picture_max_size:
                                self._p_errors = 'Picture file size is too large!'

                            # 处理图片
                            image_instance = BaseImage(image=data[perfect_file_key],
                                                       max_disk_size=self.picture_max_size)
                            # memory_picture = image_instance.clip_within_memory(goal_ratio=self.height_width_ratio)
                            disk_picture, file_path = image_instance.clip_resize(goal_width=self.max_width,
                                                                                 goal_height=self.max_height)
                            # 判断图片处理后是否大于上限
                            if BaseImage.image_disk_size(disk_picture) > self.picture_max_size:
                                self._p_errors = 'Picture file size is too large!'
                            else:
                                data[perfect_file_key] = file_path
                            picture_index += 1
                        else:
                            self._p_errors = 'Picture file format is incorrect!'
            data['picture_order_list'] = json.dumps(self.picture_order_list[:picture_index])
            data['video_order_list'] = json.dumps(self.video_list[:video_index])

            super(ClothesSerializer, self).__init__(data=data, **kwargs)
        else:
            super(ClothesSerializer, self).__init__(instance, **kwargs)

    class Meta:
        model = Clothes
        fields = '__all__'

    @property
    def data(self):
        _data = super(ClothesSerializer, self).data
        _data['picture_list'] = [_data[key] for key in _data if key in self.picture_url_list]
        _data['video_list'] = [_data['video_url']] if _data.get('video_url') else []

        for p_key in self.picture_url_list + self.picture_list + self.video_url_list + self.video_list:
            if p_key in _data:
                _data.pop(p_key)
        return _data

    def is_valid(self, raise_exception=False):
        if self._p_errors:
            self._errors = self._p_errors
            return False
        else:
            return super(ClothesSerializer, self).is_valid(raise_exception=raise_exception)

    @property
    def errors(self):
        if self._p_errors:
            return self._p_errors
        else:
            return super(ClothesSerializer, self).errors

    def update_store_clothes_active_status(self, clothes_id, validated_data):
        """
        门店的商品状态和品牌的商品状态同步，包括：上下架、是否新品、是否热销、是否促销
        :param clothes_id: 商品ID 
        :param validated_data: 商品状态：上下架、是否新品、是否热销、是否促销
        :return: 
        """
        sync_fields = ('is_new', 'is_active', 'is_hot_sale', 'is_discount')

        kwargs = {'clothes_id': clothes_id}
        validated_data = {key: validated_data[key] for key in sync_fields if key in validated_data}
        if not validated_data:
            return None
        instances = StoresClothes.filter_objects(translate_cos_url=False, **kwargs)
        return StoreClothesAction().bulk_update(instances, validated_data)

    def update(self, instance, validated_data):
        # 判断instance是否是StoresClothes的model对象
        if isinstance(instance, StoresClothes):
            serializer = StoreClothesSerializer(instance)
            return serializer.update(instance, validated_data)

        # 更新Clothes的model对象
        pop_keys = ['id', 'pk', 'clothes_id']
        for p_key in pop_keys:
            if p_key in validated_data:
                validated_data.pop(p_key)

        # "上下架状态"和"是否在小程序端展示"联动
        is_active = does_display_wechat = validated_data.get('is_active', -1)
        if is_active != -1:
            validated_data['is_active'] = is_active
            validated_data['does_display_wechat'] = does_display_wechat

        # 品牌的商品状态和门店同步
        update_store_clothes_result = self.update_store_clothes_active_status(instance.id, validated_data)
        if isinstance(update_store_clothes_result, Exception):
            raise update_store_clothes_result

        error_message = 'present_price can not greater than original_price!'
        original_price = validated_data.get('original_price', instance.original_price)
        present_price = validated_data.get('present_price', instance.present_price)
        if decimal.Decimal(present_price) > decimal.Decimal(original_price):
            raise Exception(error_message)
        else:
            if 'is_discount' not in validated_data:
                validated_data['is_discount'] = 1

        # 视频有更新
        if 'video' in validated_data:
            if validated_data['video'].name.upper().split('.')[-1] in self.video_postfix_list:
                if validated_data['video'].size > self.video_max_size:
                    raise Exception('Video file size is too large!')
                else:
                    perfect_key = 'video_url'
                    validated_data[perfect_key] = BaseImage.save_file_to_disk_for_in_memory_uploaded_file(
                        validated_data.pop('video')
                    )
            else:
                raise Exception('Video file format is incorrect!')

        # 图片有更新
        if 'picture_order_list' in validated_data:
            if instance.picture_order_list != validated_data['picture_order_list']:
                ins_order_list = json.loads(instance.picture_order_list)
                val_order_list = json.loads(validated_data['picture_order_list'])
                added_list = list(set(val_order_list) - set(ins_order_list))
                union_list = list(set(val_order_list) & set(ins_order_list))
                diff_list = sorted(list(set(self.picture_list) - set(union_list)))

                picture_ins_dict = {}
                for index, item in enumerate(added_list, 1):
                    key = 'picture%d' % index
                    picture = validated_data.pop(key)
                    # 判断图片源文件大小是否超过规定的上限
                    if picture.size > self.original_picture_max_size:
                        raise Exception('Picture file size is too large!',)

                    # 处理图片
                    image_instance = BaseImage(image=picture,
                                               max_disk_size=self.picture_max_size)
                    disk_picture, file_path = image_instance.clip_resize(goal_width=self.max_width,
                                                                         goal_height=self.max_height)
                    # 判断图片处理后是否大于上限
                    if BaseImage.image_disk_size(disk_picture) > self.picture_max_size:
                        raise Exception('Picture file size is too large!', )
                    else:
                        picture_ins_dict[key] = file_path

                new_order_list = [item for item in val_order_list if item in union_list]
                dict_keys = list(picture_ins_dict.keys())
                for index, value in enumerate(diff_list, 1):
                    if index > len(dict_keys):
                        break
                    perfect_key = '%s_url' % value
                    validated_data[perfect_key] = picture_ins_dict[dict_keys[index-1]]
                    new_order_list.append(value)
                validated_data['picture_order_list'] = json.dumps(new_order_list)

        return super(ClothesSerializer, self).update(instance, validated_data)

    def delete(self, instance):
        validated_data = {'status': instance.id + 1}
        return super(ClothesSerializer, self).update(instance, validated_data)

    def batch_update(self, request, instance_ids, validated_data):
        return self.Meta.model.batch_update(request, instance_ids, validated_data)


class ClothesResponseSerializer(BaseSerializer):
    id = serializers.IntegerField()
    clothes_id = serializers.IntegerField()
    main_sku_code = serializers.CharField(allow_null=True, allow_blank=True)
    business_user_id = serializers.IntegerField()
    title = serializers.CharField()
    subtitle = serializers.CharField(allow_blank=True, allow_null=True)
    description = serializers.CharField(allow_blank=True, allow_null=True)
    recommend_title = serializers.CharField(allow_blank=True, allow_null=True)
    recommend_subtitle = serializers.CharField(allow_blank=True, allow_null=True)

    goods_id = serializers.CharField()
    original_price = serializers.CharField()
    present_price = serializers.CharField()
    # 商品上架、下架状态
    is_active = serializers.IntegerField()
    # 商品是否状态
    is_new = serializers.IntegerField()
    # 商品是否热卖状态
    is_hot_sale = serializers.IntegerField()
    # 商品是否打折状态
    is_discount = serializers.IntegerField()
    # 数据状态：1：正常 其他值：已删除
    status = serializers.IntegerField()

    # 服装适合性别：1：男装 2：女装
    gender = serializers.IntegerField()
    # 服装适合人群 1：成人 2：儿童
    # crowd = serializers.IntegerField()
    # 服装类别：例如（裙子，短袖、长裤等）
    # category = serializers.CharField()
    # 服装适合体型：A1：瘦  A2：匀称  A3：胖
    #            B1：瘦  B2：匀称  B3：胖
    #            C1：瘦  C2：匀称  C3：胖
    # 字段值：JSON字符串，如：'["A1", "B2", "C3"]'
    shape = serializers.ListField()
    # 图片保存顺序
    picture_order_list = serializers.ListField()
    # 视频读取、存储顺序
    video_order_list = serializers.ListField()

    video_list = serializers.ListField(allow_null=True)
    picture_list = serializers.ListField(allow_null=True)

    # 标签  如：1：显瘦 2：百搭 3：基本款
    # 字段值：JSON字符串，如：'[1, 2, 3]'
    tags = serializers.ListField()
    color = serializers.CharField(allow_null=True, allow_blank=True)
    # 是否终端展示  0: 不展示  1：展示
    # 字段值：JSON字符串，如：'{"new": 0,
    #                       "discount": 1,
    #                       "hot_sale": 1}'
    does_display_mirror = serializers.DictField()
    # 小程序端展示  0：不展示  1：展示
    does_display_wechat = serializers.IntegerField()
    # 大分类代码
    large_classify_code = serializers.CharField()
    # 大分类名称
    large_classify_name = serializers.CharField()
    # 中分类代码
    middle_classify_code = serializers.CharField()
    # 中分类名称
    middle_classify_name = serializers.CharField()

    # 商品属性
    fabric_component = serializers.CharField(allow_null=True, allow_blank=True)
    stereotype = serializers.CharField(allow_null=True, allow_blank=True)
    thickness = serializers.CharField(allow_null=True, allow_blank=True)
    elastic = serializers.CharField(allow_null=True, allow_blank=True)

    # 服装颜色（智能匹配时使用）
    clothes_color = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    clothes_color_id = serializers.IntegerField(allow_null=True, required=False)
    # 服装风格（智能匹配时使用）
    clothes_style = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    clothes_style_id = serializers.IntegerField(allow_null=True, required=False)

    created = serializers.DateTimeField()
    updated = serializers.DateTimeField()


class ClothesListSerializer(BaseListSerializer):
    child = ClothesResponseSerializer()


class ClothesNumberSerializer(BaseSerializer):
    all = serializers.IntegerField()
    active = serializers.IntegerField()
    inactive = serializers.IntegerField()
    new = serializers.IntegerField()
    not_new = serializers.IntegerField()
    hot_sale = serializers.IntegerField()
    not_hot_sale = serializers.IntegerField()


class AdvertisingCopySerializer(BaseModelSerializer):
    def __init__(self, instance=None, data=None, request=None, **kwargs):
        if data:
            data['business_user_id'] = request.user.id
            super(AdvertisingCopySerializer, self).__init__(data=data, **kwargs)
        else:
            super(AdvertisingCopySerializer, self).__init__(instance, **kwargs)

    class Meta:
        model = AdvertisingCopy
        fields = '__all__'

    def delete(self, instance):
        validated_data = {'status': instance.id + 1}
        return self.update(instance, validated_data)


class AdvertisingCopyListSerializer(BaseListSerializer):
    child = AdvertisingCopySerializer()


class ClothesLargeClassifySerializer(BaseModelSerializer):
    class Meta:
        model = ClothesLargeClassify
        fields = '__all__'


class ClothesLargeClassifyListSerializer(BaseListSerializer):
    child = ClothesLargeClassifySerializer()


class ClothesMiddleClassifySerializer(BaseModelSerializer):
    class Meta:
        model = ClothesMiddleClassify
        fields = '__all__'


class ClothesMiddleClassifyListSerializer(BaseListSerializer):
    child = ClothesMiddleClassifySerializer()


class BatchUploadFileTemplateSerializer(BaseModelSerializer):
    class Meta:
        model = BatchUploadFileTemplate
        fields = '__all__'


class StoreSerializer(BaseSerializer):
    brand_id = serializers.IntegerField()
    brand_name = serializers.CharField()
    business_user_id = serializers.IntegerField()
    store_name = serializers.CharField()
    province = serializers.CharField()
    city = serializers.CharField()
    county = serializers.CharField()
    address = serializers.CharField()

    # 门店状态  0: 未开业  1：已开业 2：已撤店
    active_status = serializers.IntegerField()
    # 数据状态，1：正常  其他值：已删除
    status = serializers.IntegerField()
    created = serializers.DateTimeField()
    updated = serializers.DateTimeField()


class StoreListSerializer(BaseListSerializer):
    child = StoreSerializer()


class MirrorClothesManageDetailSerializer(BaseSerializer):
    id = serializers.IntegerField()
    clothes_id = serializers.IntegerField()
    main_sku_code = serializers.CharField(allow_null=True, allow_blank=True)
    goods_id = serializers.CharField()
    title = serializers.CharField()
    # 是否终端展示  0: 不展示  1：展示
    # 字段值：JSON字符串，如：'{"new": 0,
    #                       "discount": 1,
    #                       "hot_sale": 1}'
    does_display_mirror = serializers.DictField()
    # 商品是否新品状态
    is_new = serializers.IntegerField()
    # 商品是否打折状态
    is_discount = serializers.IntegerField()


class MirrorClothesManageListSerializer(BaseListSerializer):
    child = MirrorClothesManageDetailSerializer()


class MirrorClothesManageSerializer(BaseModelSerializer):
    class Meta:
        model = Clothes
        fields = '__all__'

    def update(self, instance, validated_data):
        try:
            does_display_mirror = json.loads(instance.does_display_mirror)
        except:
            does_display_mirror = {}
        does_display_mirror[validated_data['type']] = validated_data['status']
        validated_data = {'does_display_mirror': json.dumps(does_display_mirror)}
        return super(MirrorClothesManageSerializer, self).update(instance, validated_data)


class ExportFileRecordSerializer(BaseModelSerializer):
    class Meta:
        model = ExportFileRecord
        fields = '__all__'


class StoreClothesSerializer(BaseModelSerializer):
    class Meta:
        model = StoresClothes
        fields = '__all__'

    def update(self, instance, validated_data):
        pop_keys = ('pk', 'id', 'store_clothes_id')
        for p_key in pop_keys:
            if p_key in validated_data:
                validated_data.pop(p_key)

        return super(StoreClothesSerializer, self).update(instance, validated_data)


class ClothesColorSerializer(BaseModelSerializer):
    class Meta:
        model = ClothesColor
        fields = ('id', 'color')


class ClothesColorListSerializer(BaseListSerializer):
    child = ClothesColorSerializer()


class ClothesStyleSerializer(BaseModelSerializer):
    class Meta:
        model = ClothesStyle
        fields = ('id', 'style')


class ClothesStyleListSerializer(BaseListSerializer):
    child = ClothesStyleSerializer()
