# -*- coding: utf8 -*-
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

from clothes.permissions import (IsOwnerOrReadOnly,
                                 IsClothesListPermission,
                                 IsClothesBatchActionPermission)
from clothes.serializers import (ClothesSerializer,
                                 ClothesResponseSerializer,
                                 ClothesListSerializer,
                                 ClothesNumberSerializer,
                                 AdvertisingCopySerializer,
                                 ClothesLargeClassifyListSerializer,
                                 ClothesMiddleClassifyListSerializer,
                                 BatchUploadFileTemplateSerializer,
                                 StoreListSerializer,
                                 AdvertisingCopyListSerializer,
                                 MirrorClothesManageListSerializer,
                                 MirrorClothesManageSerializer,
                                 ExportFileRecordSerializer,
                                 StoreClothesSerializer,
                                 ClothesColorListSerializer,
                                 ClothesStyleListSerializer)
from clothes.models import (Clothes,
                            AdvertisingCopy,
                            ClothesLargeClassify,
                            ClothesMiddleClassify,
                            BatchUploadFileTemplate,
                            ExportFileRecord,
                            StoresClothes,
                            ClothesColor,
                            ClothesStyle)
from clothes.forms import (ClothesCreateForm,
                           ClothesUpdateForm,
                           ClothesDeleteForm,
                           ClothesDetailForm,
                           ClothesListForm,
                           ClothesBatchCreateForm,
                           ClothesBatchUpdateForm,
                           ClothesNumberDetailForm,
                           AdvertisingCopyCreateForm,
                           AdvertisingCopyUpdateForm,
                           AdvertisingCopyDeleteForm,
                           AdvertisingCopyDetailForm,
                           ClothesLargeClassifyListForm,
                           ClothesMiddleClassifyListForm,
                           ClothesBatchCreateColumnDetailForm,
                           BatchUploadFileTemplateForm,
                           StoreListForm,
                           AdvertisingCopyListForm,
                           MirrorClothesManageListForm,
                           MirrorClothesManageActionForm,
                           ExportFileActionForm,
                           BatchUploadImageForm,
                           BatchClaimClothesActionForm,
                           BatchClaimClothesColumnDetailForm,
                           ClothesColorListForm,
                           ClothesStyleListForm)
from horizon.views import (FMActionAPIView,
                           FMDetailAPIView,
                           FMListAPIView)
from horizon.permission import DjangoAPIPermissionOrAnonReadOnly
from Admin_App.ad_stores.models import Store, Brand

from horizon.http import status as fm_status
from horizon import main

import json
import xlrd
import csv
from io import StringIO
import io
import os
import decimal
from decimal import Decimal


class ClothesAction(FMActionAPIView):
    """
    服装数据创建、更新及删除
    """
    post_form_class = ClothesCreateForm
    post_serializer_class = ClothesSerializer
    put_form_class = ClothesUpdateForm
    put_serializer_class = ClothesSerializer
    delete_form_class = ClothesDeleteForm
    delete_serializer_class = ClothesSerializer
    model_class = Clothes
    permission_classes = (DjangoAPIPermissionOrAnonReadOnly, IsOwnerOrReadOnly)

    def is_request_data_valid(self, **kwargs):
        json_fields = ('shape', 'picture_order_list', 'video_order_list', 'tags', 'does_display_mirror')
        for field in json_fields:
            if field in kwargs:
                try:
                    json.loads(kwargs[field])
                except Exception as e:
                    return False, 'Params [%s] data is incorrect: %s' % (field, e.args)

        if 'classify_id' in kwargs:
            instance = ClothesMiddleClassify.get_object(pk=kwargs['classify_id'])
            if isinstance(instance, Exception):
                return False, 'Params [classify_id] data is incorrect: %s' % instance.args

        unequal_error_message = 'Params [is_active] and [does_display_wechat] must be equal.'
        # "上下架状态"和"是否在小程序端展示"联动
        if 'is_active' in kwargs:
            if 'does_display_wechat' in kwargs:
                if kwargs['is_active'] != kwargs['does_display_wechat']:
                    return False, unequal_error_message
        elif 'does_display_wechat' in kwargs:
            return False, unequal_error_message
        return True, None

    def get_instance(self, request, pk):
        kwargs = {'pk': pk}
        return self.model_class.get_object(request=request, translate_cos_url=False, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        创建服装信息
        :param request: 
        :param args: 
        :param kwargs: 
        :return: 
        """
        return super(ClothesAction, self).post(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        """
        更新服装信息
        :param request: 
        :param args: 
        :param kwargs: 
        :return: 
        """
        return super(ClothesAction, self).put(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """
        删除服装信息
        :param request: 
        :param args: 
        :param kwargs: 
        :return: 
        """
        return super(ClothesAction, self).delete(request, *args, **kwargs)


class ClothesDetail(FMDetailAPIView):
    detail_form_class = ClothesDetailForm
    detail_serializer_class = ClothesResponseSerializer
    model_class = Clothes

    def get_instance(self, request, **kwargs):
        return self.model_class.get_detail(request, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        获取服装详情
        :param request: 
        :param args: 
        :param kwargs: 
        :return: 
        """
        return super(ClothesDetail, self).post(request, *args, **kwargs)


class ClothesList(FMListAPIView):
    list_form_class = ClothesListForm
    list_serializer_class = ClothesListSerializer
    model_class = Clothes

    def is_request_data_valid(self, request=None, **kwargs):
        if request.user.is_root_user:
            if 'business_user_id' not in kwargs:
                return False, 'Params ["business_user_id"] is required'
        return True, None

    def get_instances_list(self, request, **kwargs):
        classify_id = []
        if 'middle_classify_id' in kwargs:
            middle_classify_ins = ClothesMiddleClassify.get_object(pk=kwargs['middle_classify_id'])
            classify_id = [middle_classify_ins.id]
            kwargs.pop('middle_classify_id')
        elif 'large_classify_id' in kwargs:
            large_classify_ins = ClothesLargeClassify.get_object(pk=kwargs['large_classify_id'])
            _kwargs = {'large_classify_id': large_classify_ins.id}
            middle_classify_ins = ClothesMiddleClassify.filter_objects(**_kwargs)
            classify_id = [ins.id for ins in middle_classify_ins]
            kwargs.pop('large_classify_id')

        if classify_id:
            kwargs['classify_id__in'] = classify_id

        return self.model_class.filter_details(request, fuzzy=True, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        获取服装详情列表
        :param request: 
        :param args: 
        :param kwargs: 
        :return: 
        """
        return super(ClothesList, self).post(request, *args, **kwargs)


class ClothesBatchAction(generics.GenericAPIView):
    """
    批量添加、修改服装数据
    """
    permission_classes = (IsClothesBatchActionPermission, )

    execl_fields = ('title', 'goods_id', 'original_price', 'present_price', 'gender', 'color',
                    'large_classify_name', 'middle_classify_name', 'is_active', 'is_new',
                    'is_discount', 'is_hot_sale', 'description', 'tags', 'fabric_component',
                    'stereotype', 'thickness', 'elastic', 'recommend_title', 'recommend_subtitle')
    column_gender_dict = {'男': 1, '女': 2, '中性': 3}
    column_is_column_dict = {'否': 0, '是': 1, '': 0, 1: 1, 0: 0}

    def make_perfect_init_data(self, request, validated_data):
        if not validated_data['present_price']:
            validated_data['present_price'] = validated_data['original_price']

        # 判断现价是否大于原价
        if Decimal(validated_data['present_price']) > Decimal(validated_data['original_price']):
            return Exception('present_price can not greater than original_price!')
        elif Decimal(validated_data['present_price']) < Decimal(validated_data['original_price']):
            validated_data['is_discount'] = 1

        # 去掉goods_id后面的小数点（由excel软件自身问题导致）
        goods_id_list = str(validated_data['goods_id']).split('.')
        if len(goods_id_list) == 2:
            try:
                goods_id_suffix = int(goods_id_list[1])
            except:
                goods_id_suffix = None
            if goods_id_suffix == 0:
                validated_data['goods_id'] = goods_id_list[0]

        # 生成main_sku_code
        large_classify_ins = ClothesLargeClassify.get_object(classify_name=validated_data['large_classify_name'])
        if isinstance(large_classify_ins, Exception):
            return large_classify_ins
        middle_classify_ins = ClothesMiddleClassify.get_object(large_classify_id=large_classify_ins.id,
                                                               classify_name=validated_data['middle_classify_name'])
        if isinstance(middle_classify_ins, Exception):
            return middle_classify_ins

        # store_ins = Store.get_object(business_user_id=request.user.id)
        validated_data['main_sku_code'] = '%02d%02d%06d%s' % (
            middle_classify_ins.large_classify_id,
            middle_classify_ins.id,
            request.user.id,
            main.make_random_char_and_number_of_string(4))
        validated_data['classify_id'] = middle_classify_ins.id

        for key in list(validated_data.keys()):
            if key == 'gender':
                validated_data['gender'] = self.column_gender_dict.get(validated_data['gender'], 0)
            elif key in ('is_active', 'is_new', 'is_discount', 'is_hot_sale'):
                validated_data[key] = self.column_is_column_dict.get(validated_data[key], -1)
            elif key == 'tags':
                try:
                    validated_data[key] = json.dumps(validated_data[key].split(','))
                except Exception as e:
                    return e

        return validated_data

    def insert_to_db(self, request, file_content):
        insert_data = []
        # 目前支持xls和csv格式的文件

        base_table_file = main.BaseTableFile(execl_fields=self.execl_fields,
                                             perfect_detail_form_class=ClothesBatchCreateColumnDetailForm,
                                             make_perfect_init_data_function=self.make_perfect_init_data)
        if file_content._name.endswith('csv'):
            insert_data = base_table_file.read_content_for_csv(request, file_content)
        elif file_content._name.endswith('xlsx'):
            insert_data = base_table_file.read_content_for_xls(request, file_content)
        else:
            pass
        if isinstance(insert_data, Exception):
            return False, str(insert_data.args)

        return Clothes.insert_with_batch(request, insert_data)

    def is_request_data_valid(self, request, **kwargs):
        try:
            ids = json.loads(kwargs['update_ids'])
        except Exception as e:
            return False, 'Params [update_ids] is incorrect: %s' % e.args

        does_all_exist = Clothes.does_all_ids_exist(request, ids)
        if not does_all_exist:
            return False, 'Params [update_ids] data is incorrect.'
        return True, None

    def make_perfect_batch_update_data(self, **kwargs):
        perfect_data = {}
        action_dict = {'active': {'is_active': 1},
                       'inactive': {'is_active': 0},
                       'hot_sale': {'is_hot_sale': 1},
                       'not_hot_sale': {'is_hot_sale': 0},
                       'new': {'is_new': 1},
                       'not_new': {'is_new': 0},
                       'discount': {'is_discount': 1},
                       'not_discount': {'is_discount': 0},
                       }
        perfect_data.update(**action_dict[kwargs['action']])
        return perfect_data

    def post(self, request, *args, **kwargs):
        """
        批量添加
        :param request: 
        :param args: 
        :param kwargs: 
        :return: 
        """
        form = ClothesBatchCreateForm(request.data, request.FILES)
        if not form.is_valid():
            return fm_status.return_error_response(fm_status.HTTP_400_BAD_REQUEST, form.errors)

        cld = form.cleaned_data
        result, error_message = self.insert_to_db(request, cld['upload_file'])
        if not result:
            return fm_status.return_error_response(fm_status.HTTP_400_BAD_REQUEST, error_message)
        return fm_status.return_success_response()

    def put(self, request, *args, **kwargs):
        """
        批量修改服装数据
        :param request: 
        :param args: 
        :param kwargs: 
        :return: 
        """
        form = ClothesBatchUpdateForm(request.data)
        if not form.is_valid():
            return fm_status.return_error_response(fm_status.HTTP_400_BAD_REQUEST, form.errors)

        cld = form.cleaned_data
        is_valid, error_message = self.is_request_data_valid(request, **cld)
        if not is_valid:
            return fm_status.return_error_response(fm_status.HTTP_400_BAD_REQUEST, error_message)

        validated_data = self.make_perfect_batch_update_data(**cld)
        instance_ids = json.loads(cld['update_ids'])
        serializer = ClothesSerializer()
        try:
            serializer.batch_update(request, instance_ids, validated_data)
        except Exception as e:
            return fm_status.return_error_response(fm_status.HTTP_400_BAD_REQUEST, e.args)
        return fm_status.return_success_response()


class ClothesCategoryList(generics.GenericAPIView):
    """
    服装类别列表（推荐列表）
    """
    def get_category_list(self, request):
        return Clothes.get_recommend_category_list(request)

    def post(self, request, *args, **kwargs):
        """
        获取服装类别推荐列表
        :param request: 
        :param args: 
        :param kwargs: 
        :return: 
        """
        category_list = self.get_category_list(request)
        return fm_status.return_success_response(category_list)


class ClothesNumberDetail(FMDetailAPIView):
    """
    获取全部、上架及下架商品的数量
    """
    detail_form_class = ClothesNumberDetailForm
    detail_serializer_class = ClothesNumberSerializer
    model_class = Clothes

    def get_instance(self, request, **kwargs):
        return Clothes.get_clothes_number(request)

    def post(self, request, *args, **kwargs):
        """
        获取全部、上架及下架商品的数量
        :param request: 
        :param args: 
        :param kwargs: 
        :return: 
        """
        return super(ClothesNumberDetail, self).post(request, *args, **kwargs)


class AdvertisingCopyAction(FMActionAPIView):
    """
    镜子广告文案创建、更新及删除
    """
    post_form_class = AdvertisingCopyCreateForm
    post_serializer_class = AdvertisingCopySerializer
    put_form_class = AdvertisingCopyUpdateForm
    put_serializer_class = AdvertisingCopySerializer
    delete_form_class = AdvertisingCopyDeleteForm
    delete_serializer_class = AdvertisingCopySerializer
    model_class = AdvertisingCopy

    def get_instance(self, request, pk):
        kwargs = {'business_user_id': request.user.id,
                  'pk': pk}
        return self.model_class.get_object(translate_cos_url=False, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        创建广告文案
        """
        return super(AdvertisingCopyAction, self).post(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        """
        更新广告文案
        """
        return super(AdvertisingCopyAction, self).put(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """
        删除广告文案
        """
        return super(AdvertisingCopyAction, self).delete(request, *args, **kwargs)


class AdvertisingCopyDetail(FMDetailAPIView):
    """
    镜子广告文案详情
    """
    detail_form_class = AdvertisingCopyDetailForm
    detail_serializer_class = AdvertisingCopySerializer
    model_class = AdvertisingCopy

    def get_instance(self, request, **kwargs):
        kwargs['business_user_id'] = request.user.id
        return self.model_class.get_object(**kwargs)

    def post(self, request, *args, **kwargs):
        return super(AdvertisingCopyDetail, self).post(request, *args, **kwargs)


class AdvertisingCopyList(FMListAPIView):
    """
    镜子广告文案列表
    """
    list_form_class = AdvertisingCopyListForm
    list_serializer_class = AdvertisingCopyListSerializer
    model_class = AdvertisingCopy

    def get_instances_list(self, request, **kwargs):
        _kwargs = {'business_user_id': request.user.id}
        _kwargs.update(**kwargs)
        return self.model_class.filter_objects(**_kwargs)

    def post(self, request, *args, **kwargs):
        return super(AdvertisingCopyList, self).post(request, *args, **kwargs)


class ClothesLargeClassifyList(FMListAPIView):
    """
    获取服装大分类列表
    """
    list_form_class = ClothesLargeClassifyListForm
    list_serializer_class = ClothesLargeClassifyListSerializer
    model_class = ClothesLargeClassify

    def post(self, request, *args, **kwargs):
        return super(ClothesLargeClassifyList, self).post(request, *args, **kwargs)


class ClothesMiddleClassifyList(FMListAPIView):
    """
    获取服装中分类列表
    """
    list_form_class = ClothesMiddleClassifyListForm
    list_serializer_class = ClothesMiddleClassifyListSerializer
    model_class = ClothesMiddleClassify

    def get_instances_list(self, request, **kwargs):
        _kwargs = {}
        if 'large_classify_id' in kwargs:
            _kwargs = {'large_classify_id': kwargs['large_classify_id']}
        return ClothesMiddleClassify.filter_objects(**_kwargs)

    def post(self, request, *args, **kwargs):
        return super(ClothesMiddleClassifyList, self).post(request, *args, **kwargs)


class BatchUploadFileTemplateDetail(FMDetailAPIView):
    """
    获取批量上传文件模板
    """
    detail_form_class = BatchUploadFileTemplateForm
    detail_serializer_class = BatchUploadFileTemplateSerializer
    model_class = BatchUploadFileTemplate

    def post(self, request, *args, **kwargs):
        return super(BatchUploadFileTemplateDetail, self).post(request, *args, **kwargs)


class StoreList(FMListAPIView):
    """
    获取门店列表
    """
    list_form_class = StoreListForm
    list_serializer_class = StoreListSerializer
    model_class = Store

    def get_instances_list(self, request, **kwargs):
        _kwargs = {'business_user_id': request.user.id}
        return Store.filter_details(**_kwargs)

    def post(self, request, *args, **kwargs):
        return super(StoreList, self).post(request, *args, **kwargs)


class MirrorClothesManageList(FMListAPIView):
    """
    镜子管理：折扣/新品列表
    """
    list_form_class = MirrorClothesManageListForm
    list_serializer_class = MirrorClothesManageListSerializer
    model_class = Clothes

    def get_instances_list(self, request, **kwargs):
        _kwargs = {'is_active': 1}
        if kwargs['type'] == 'discount':
            _kwargs['is_discount'] = 1
        elif kwargs['type'] == 'new':
            _kwargs['is_new'] = 1

        details = self.model_class.filter_details(request, **_kwargs)
        return sorted(details, key=lambda x: x['does_display_mirror'].get(kwargs['type'], 0), reverse=True)

    def get_perfect_request_data(self, **kwargs):
        if 'page_size' not in kwargs:
            kwargs['page_size'] = settings.MAX_PAGE_SIZE
        return kwargs

    def post(self, request, *args, **kwargs):
        return super(MirrorClothesManageList, self).post(request, *args, **kwargs)


class MirrorClothesManageAction(FMActionAPIView):
    """
    镜子管理：折扣系列、最新搭配设置是否在镜子端展示
    """
    put_form_class = MirrorClothesManageActionForm
    put_serializer_class = MirrorClothesManageSerializer
    model_class = Clothes

    def get_instance(self, request, pk):
        kwargs = {'business_user_id': request.user.id,
                  'pk': pk}
        return self.model_class.get_object(request=request, translate_cos_url=False, **kwargs)

    def put(self, request, *args, **kwargs):
        """
        更新是否在镜子端显示的状态
        """
        return super(MirrorClothesManageAction, self).put(request, *args, **kwargs)


class ExportFileDetail(FMDetailAPIView):
    """
    批量下载商品数据
    """
    detail_form_class = ExportFileActionForm
    detail_serializer_class = ExportFileRecordSerializer
    model_class = ExportFileRecord
    column_names = ('编码(main_sku_code)', '货号', '商品名称', '性别定位', '颜色', '原价', '现价', '是否上线',
                    '是否新品', '是否促销', '是否热销', '大分类名称', '中分类名称', '描述字段', '标签', '是否小程序展示',
                    '面料成分', '版型', '薄厚', '弹性', '推荐理由', '推荐理由-详细')
    column_name_keys = ('main_sku_code', 'goods_id', 'title', 'gender', 'color', 'original_price', 'present_price',
                        'is_active', 'is_new', 'is_discount', 'is_hot_sale', 'large_classify_name',
                        'middle_classify_name', 'description', 'tags', 'does_display_wechat',
                        'fabric_component', 'stereotype', 'thickness', 'elastic',
                        'recommend_title', 'recommend_subtitle')
    column_gender_dict = {1: '男', 2: '女', 3: '中性'}
    column_is_column_dict = {0: '否', 1: '是'}

    def make_csv_file_with_disk(self, data_list):
        file_path = main.make_no_repeat_image_name(image_format='CSV')
        media_path = os.path.join(settings.MEDIA_ROOT, settings.PICTURE_DIRS['business']['clothes'])
        file_path = os.path.join(media_path, file_path)

        perfect_data_list = []
        for item in data_list:
            item_list = []
            for key in self.column_name_keys:
                if key == 'gender':
                    value = self.column_gender_dict[item[key]]
                elif key in ('is_discount', 'is_new', 'is_active', 'is_hot_sale', 'does_display_wechat'):
                    value = self.column_is_column_dict[item[key]]
                elif key == 'tags':
                    value = ','.join(item[key])
                else:
                    value = item[key]
                item_list.append(value)
            perfect_data_list.append(item_list)

        with open(file_path, "w") as fp:
            writer = csv.writer(fp)
            # 先写入columns_name
            writer.writerow(self.column_names)
            # 写入多行用writerows
            writer.writerows(perfect_data_list)
        return file_path

    def get_instance(self, request, **kwargs):
        # 获取全部商品数据
        if kwargs['type'] == 'all':
            data_list = Clothes.filter_details(request)
        elif kwargs['type'] == 'screen':
            data_list = Clothes.filter_details(request, fuzzy=True, **kwargs)
        else:
            # 获取选中部分的数据
            _kwargs = {'id__in': json.loads(kwargs['ids'])}
            data_list = Clothes.filter_details(request, **_kwargs)

        # 生成csv文件
        file_path = self.make_csv_file_with_disk(data_list)
        init_data = {'file_url': file_path}
        serializer = ExportFileRecordSerializer(data=init_data)
        if not serializer.is_valid():
            return Exception(serializer.errors)
        try:
            instance = serializer.save()
        except Exception as e:
            return e
        return self.model_class.get_object(pk=instance.id)

    def is_request_data_valid(self, **kwargs):
        if kwargs['type'] == 'select':
            if 'ids' not in kwargs:
                return False, 'Params ["ids"] is required when Params ["type"] value is "select"'

        if 'ids' in kwargs:
            try:
                json.loads(kwargs['ids'])
            except Exception as e:
                return False, e.args
        return True, None

    def post(self, request, *args, **kwargs):
        return super(ExportFileDetail, self).post(request, *args, **kwargs)


class BatchUploadImageAction(generics.GenericAPIView):
    """
    批量上传商品图片
    """
    post_form_class = BatchUploadImageForm

    def update_image_to_db(self, request, image_name_list):
        """
        :param request: 
        :param image_name_list: ['dir_path', ['child_path', ...], [file_name, ...]]
        :return: 
        """
        picture_order_list = ['picture1', 'picture2', 'picture3', 'picture4']
        picture_url_list = ['picture1_url', 'picture2_url', 'picture3_url', 'picture4_url']
        update_image_dict = {}
        for dir_file_list in image_name_list:
            for image_name in dir_file_list[2]:
                if image_name.startswith('.'):
                    continue
                goods_id, save_order = image_name.split('.', 1)[0].split('_')
                item_list = update_image_dict.get(goods_id, [])
                item_list.append(os.path.join(dir_file_list[0].split('static/', 1)[1], image_name))
                update_image_dict[goods_id] = sorted(item_list)

        perfect_image_dict = {}
        for goods_id, item_list in update_image_dict.items():
            validated_data = {'picture_order_list': json.dumps(picture_order_list[:len(item_list)])}
            for index, item in enumerate(item_list):
                validated_data[picture_url_list[index]] = item
            perfect_image_dict[goods_id] = validated_data

        try:
            instances = Clothes.batch_update_image(request, perfect_image_dict)
        except Exception as e:
            return e
        return instances

    def upload_image(self, request, compressed_file):
        file_name = main.save_django_upload_file_to_disk(compressed_file)
        if compressed_file.name.endswith('.tar.gz'):
            unzip_dir_name = main.BaseUnzip.un_tar_gz(file_name)
        elif compressed_file.name.endswith('.rar'):
            unzip_dir_name = main.BaseUnzip.un_rar(file_name)
        elif compressed_file.name.endswith('.tar'):
            unzip_dir_name = main.BaseUnzip.un_tar(file_name)
        elif compressed_file.name.endswith('.zip'):
            unzip_dir_name = main.BaseUnzip.un_zip(file_name)
        else:
            return False, 'Params [compressed_file] data is incorrect.'

        # 获取所有需要上传的图片
        image_name_list = []
        for item in os.walk(unzip_dir_name):
            image_name_list.append(item)
        result = self.update_image_to_db(request, image_name_list)
        if isinstance(result, Exception):
            return False, result.args
        return True, None

    def post(self, request, *args, **kwargs):
        form = BatchUploadImageForm(request.data, request.FILES)
        if not form.is_valid():
            return fm_status.return_error_response(fm_status.HTTP_400_BAD_REQUEST, form.errors)

        cld = form.cleaned_data
        result, error_message = self.upload_image(request, cld['compressed_file'])
        if not result:
            return fm_status.return_error_response(fm_status.HTTP_400_BAD_REQUEST, error_message)
        return fm_status.return_success_response()


class BatchClaimClothesAction(generics.GenericAPIView):
    """
    批量认领商品（门店认领品牌录入的商品）
    """
    post_form_class = BatchClaimClothesActionForm
    execl_fields = ('goods_id',)

    def make_perfect_init_data(self, request, validated_data):
        # 去掉goods_id后面的小数点（由excel软件自身问题导致）
        goods_id_list = str(validated_data['goods_id']).split('.')
        if len(goods_id_list) == 2:
            try:
                goods_id_suffix = int(goods_id_list[1])
            except:
                goods_id_suffix = None
            if goods_id_suffix == 0:
                validated_data['goods_id'] = goods_id_list[0]
        return validated_data

    def batch_claim_clothes(self, request, file_content):
        insert_data = []
        # 目前支持xls和csv格式的文件

        base_table_file = main.BaseTableFile(execl_fields=self.execl_fields,
                                             perfect_detail_form_class=BatchClaimClothesColumnDetailForm,
                                             make_perfect_init_data_function=self.make_perfect_init_data)
        if file_content._name.endswith('csv'):
            insert_data = base_table_file.read_content_for_csv(request, file_content)
        elif file_content._name.endswith('xlsx'):
            insert_data = base_table_file.read_content_for_xls(request, file_content)
        else:
            pass
        if isinstance(insert_data, Exception):
            return insert_data
        return StoresClothes.claim_clothes_for_store(request, insert_data)

    def post(self, request, *args, **kwargs):
        form = BatchClaimClothesActionForm(request.data, request.FILES)
        if not form.is_valid():
            return fm_status.return_error_response(fm_status.HTTP_400_BAD_REQUEST, form.errors)

        cld = form.cleaned_data
        result = self.batch_claim_clothes(request, cld['claim_file'])
        if isinstance(result, Exception):
            return fm_status.return_error_response(fm_status.HTTP_400_BAD_REQUEST, str(result.args))
        return fm_status.return_success_response()


class ClothesColorList(FMListAPIView):
    """
    衣服颜色列表
    """
    list_form_class = ClothesColorListForm
    list_serializer_class = ClothesColorListSerializer
    model_class = ClothesColor

    def post(self, request, *args, **kwargs):
        """
        获取衣服颜色列表
        :param request: 
        :param args: 
        :param kwargs: 
        :return: 
        """
        return super(ClothesColorList, self).post(request, *args, **kwargs)


class ClothesStyleList(FMListAPIView):
    """
    服装风格列表
    """
    list_form_class = ClothesStyleListForm
    list_serializer_class = ClothesStyleListSerializer
    model_class = ClothesStyle

    def post(self, request, *args, **kwargs):
        """
        获取服装风格列表
        :param request: 
        :param args: 
        :param kwargs: 
        :return: 
        """
        return super(ClothesStyleList, self).post(request, *args, **kwargs)
