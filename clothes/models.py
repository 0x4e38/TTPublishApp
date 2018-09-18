# -*- coding:utf8 -*-
from django.db import models
from django.utils.timezone import now
from django.conf import settings
from django.db.models import Q
from django.db import transaction

from horizon.models import (BaseManager,
                            model_to_dict,
                            get_perfect_filter_params)
from horizon.mixins import BaseModelMixin
from users.models import BusinessUserBind

import datetime
import re
import os
import json

CLOTHES_PICTURE_PATH = settings.PICTURE_DIRS['business']['clothes']


class ClothesColor(BaseModelMixin, models.Model):
    """
    服装颜色（智能匹配使用）
    """
    color = models.CharField('衣服颜色', max_length=16, unique=True)
    created = models.DateTimeField('创建时间', default=now)
    updated = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'fm_clothes_color'

    def __unicode__(self):
        return self.color


class ClothesStyle(BaseModelMixin, models.Model):
    """
    服装风格（智能匹配使用）
    """
    style = models.CharField('服装风格', max_length=32, unique=True)
    created = models.DateTimeField('创建时间', default=now)
    updated = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'fm_clothes_style'

    def __unicode__(self):
        return self.style


class SkinStyleMatch(BaseModelMixin, models.Model):
    """
    肤色-风格匹配
    """
    skin = models.CharField('肤色', max_length=16)
    style_id = models.IntegerField('服装风格')
    match_score = models.FloatField('肤色-风格匹配分数')
    created = models.DateTimeField('创建时间', default=now)
    updated = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'fm_skin_style_match'

    def __unicode__(self):
        return '%s-%s' % (self.skin, self.style_id)


class ClothesColorMatch(BaseModelMixin, models.Model):
    """
    衣服颜色-推荐衣服颜色匹配
    """
    clothes_color_id = models.IntegerField('衣服颜色ID')
    recommend_color_id = models.IntegerField('推荐衣服颜色ID')
    match_score = models.FloatField('衣服颜色-推荐衣服颜色匹配分数')
    created = models.DateTimeField('创建时间', default=now)
    updated = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'fm_clothes_color_match'

    def __unicode__(self):
        return '%s-%s' % (self.clothes_color_id, self.recommend_color_id)


class Clothes(BaseModelMixin, models.Model):
    """
    品牌商品数据
    """
    main_sku_code = models.CharField(u'唯一编码', max_length=32, unique=True)
    business_user_id = models.IntegerField(u'品牌商户ID', db_index=True)
    title = models.CharField(u'商品名称', max_length=128)
    subtitle = models.CharField(u'商品副标题', max_length=256, null=True, blank=True, default='')
    description = models.CharField(u'商品描述', max_length=512, null=True, blank=True, default='')
    recommend_title = models.CharField(u'推荐理由', max_length=32, null=True, blank=True, default='')
    recommend_subtitle = models.CharField(u'推荐理由-详细', max_length=64, null=True, blank=True, default='')
    # 标签  如：1：显瘦 2：百搭 3：基本款
    # 字段值：JSON字符串，如：'[1, 2, 3]'
    tags = models.CharField(u'标签', max_length=256, null=True, blank=True, default='[]')

    goods_id = models.CharField(u'商品ID/货号', max_length=64)
    original_price = models.CharField(u'原价', max_length=11)
    present_price = models.CharField(u'现价', max_length=11)
    color = models.CharField(u'颜色', max_length=32, null=True)
    # 商品上架、下架状态  0：下架 1：上架
    is_active = models.SmallIntegerField(u'上架/下架状态', default=1)
    # 商品是否是新品     0：否   1：是
    is_new = models.SmallIntegerField(u'是否是新品', default=1)
    # 商品是否是热销商品  0：否   1：是
    is_hot_sale = models.SmallIntegerField(u'是否是热销商品', default=1)
    # 是否打折   0: 否 1：是
    is_discount = models.SmallIntegerField(u'是否打折促销', default=0)
    # 数据状态：1：正常 其他值：已删除
    status = models.IntegerField(u'数据状态', default=1)

    # 服装适合性别：1：男装 2：女装  3：中性
    gender = models.SmallIntegerField(u'服装适合性别（男装、女装）', default=2)
    # 服装适合人群 1：成人 2：儿童
    crowd = models.SmallIntegerField(u'适合人群', default=1)
    # 服装类别：例如（裙子，短袖、长裤等）
    category = models.CharField(u'服装类别', max_length=64, null=True, blank=True, default='')
    # 服装适合体型：A1：瘦  A2：匀称  A3：胖
    #            B1：瘦  B2：匀称  B3：胖
    #            C1：瘦  C2：匀称  C3：胖
    # 字段值：JSON字符串，如：'["A1", "B2", "C3"]'
    shape = models.CharField(u'适合体型', max_length=64, null=True, blank=True, default='[]')
    # # 尺寸
    # size = models.CharField(u'尺寸', max_length=32, default='M')
    # 所属中分类ID
    classify_id = models.IntegerField(u'所属中分类ID')
    # 是否终端展示  0: 不展示  1：展示
    # 字段值：JSON字符串，如：'{"new": 0,
    #                       "discount": 1,
    #                       "hot_sale": 1}'
    does_display_mirror = models.CharField(u'是否终端展示',
                                           max_length=64,
                                           default='{"new": 0, "discount": 0, "hot_sale": 0}')
    # 小程序端展示  0：不展示  1：展示
    does_display_wechat = models.SmallIntegerField(u'小程序端是否展示', default=1)

    # 商品属性
    fabric_component = models.CharField(u'面料成分', max_length=64, null=True, blank=True, default='')
    stereotype = models.CharField(u'版型', max_length=48, null=True, blank=True, default='')
    thickness = models.CharField(u'厚薄', max_length=32, null=True, blank=True, default='')
    elastic = models.CharField(u'弹性', max_length=48, null=True, blank=True, default='')

    video_url = models.CharField(u'视频', max_length=200, null=True, blank=True)
    picture1_url = models.CharField(u'图1', max_length=200, null=True, blank=True)
    picture2_url = models.CharField(u'图2', max_length=200, null=True, blank=True)
    picture3_url = models.CharField(u'图3', max_length=200, null=True, blank=True)
    picture4_url = models.CharField(u'图4', max_length=200, null=True, blank=True)
    # detail_picture = models.CharField(u'原图', max_length=300)
    # 图片读取顺序，字段类型：JSON字符串，形如：
    #            '["picture1", "picture2", "picture3", "picture4"]'
    picture_order_list = models.CharField(u'图片读取顺序', max_length=128, default='[]')
    # 视频读取、存储顺序，字段类型：JSON字符串：形如：
    #            '["video"]'
    video_order_list = models.CharField(u'视频存储、读取顺序', max_length=128, default='[]')
    # 衣服颜色（智能匹配使用）
    clothes_color_id = models.IntegerField(u'衣服颜色', null=True)
    # 衣服风格（智能匹配使用）
    clothes_style_id = models.IntegerField(u'衣服风格', null=True)

    created = models.DateTimeField(u'创建时间', default=now)
    updated = models.DateTimeField(u'最后更新时间', auto_now=True)

    objects = BaseManager()

    class Meta:
        db_table = 'fm_clothes'
        unique_together = ('business_user_id', 'goods_id', 'status')
        ordering = ('-created',)

    class FMMeta:
        q_fuzzy_fields = ('title', 'goods_id')
        fuzzy_fields = ('title', )
        json_fields = ('shape', 'picture_order_list', 'video_order_list', 'tags', 'does_display_mirror')
        foreign_key_fields = (
            {'foreign_key': 'clothes_color_id',
             'field': 'clothes_color',
             'model': ClothesColor,
             'name': 'color'},
            {'foreign_key': 'clothes_style_id',
             'field': 'clothes_style',
             'model': ClothesStyle,
             'name': 'style'},
        )

    def __unicode__(self):
        return self.goods_id

    def get_perfect_file_key(self, file_key):
        return '%s_url' % file_key

    @property
    def perfect_detail(self):
        picture_list = ('picture1', 'picture2', 'picture3', 'picture4')
        video_list = ('video',)

        detail = super(Clothes, self).perfect_detail
        for key in list(detail.keys()):
            if key in self.FMMeta.json_fields:
                if detail[key]:
                    detail[key] = json.loads(detail[key])
                else:
                    if key == 'does_display_mirror':
                        detail[key] = {}
                    else:
                        detail[key] = []

        for item in self.FMMeta.foreign_key_fields:
            foreign_key_value = getattr(self, item['foreign_key'])
            if foreign_key_value:
                instance = item['model'].get_object(pk=foreign_key_value)
                detail[item['field']] = getattr(instance, item['name'])

        detail['clothes_id'] = detail['id']
        detail['picture_list'] = []
        for p_key in detail['picture_order_list']:
            perfect_key = self.get_perfect_file_key(p_key)
            if detail.get(perfect_key):
                detail['picture_list'].append(detail[perfect_key])
        detail['video_list'] = []
        for p_key in detail['video_order_list']:
            perfect_key = self.get_perfect_file_key(p_key)
            if detail.get(perfect_key):
                detail['video_list'].append(detail[perfect_key])
        for p_key in picture_list + video_list:
            perfect_key = self.get_perfect_file_key(p_key)
            if perfect_key in detail:
                detail.pop(perfect_key)

        if self.classify_id:
            classify_detail = ClothesMiddleClassify.get_detail(pk=self.classify_id)
            update_detail = {'large_classify_code': classify_detail['large_classify_code'],
                             'large_classify_name': classify_detail['large_classify_name'],
                             'middle_classify_code': classify_detail['classify_code'],
                             'middle_classify_name': classify_detail['classify_name']}
            detail.update(**update_detail)
        return detail

    @classmethod
    def get_object(cls, *args, request=None, translate_cos_url=True, **kwargs):
        if not request:
            return super(Clothes, cls).get_object(*args, translate_cos_url=translate_cos_url, **kwargs)
        else:
            # 品牌用户或root用户
            if not request.user.is_store_user:
                return super(Clothes, cls).get_object(*args, translate_cos_url=False, **kwargs)
            # 门店用户
            else:
                return StoresClothes.get_object(*args, translate_cos_url=False, **kwargs)

    @classmethod
    def get_detail(cls, request, **kwargs):
        # 品牌用户或root用户
        if not request.user.is_store_user:
            return super(Clothes, cls).get_detail(**kwargs)
        # 门店用户
        else:
            return StoresClothes.get_detail(**kwargs)

    @classmethod
    def filter_details(cls, request, fuzzy=False, **kwargs):
        args = []
        if fuzzy:
            for key in list(kwargs.keys()):
                if key in cls.FMMeta.fuzzy_fields:
                    # if key in cls.FMMeta.q_fuzzy_fields:
                    #     q_kwargs = {('%s__contains' % key): kwargs[key]}
                    #     q_str = "Q(%s__contains='%s')" % (key, kwargs[key])
                    #     args.append(q_str)
                    # else:
                    kwargs['%s__contains' % key] = kwargs[key]
                    kwargs.pop(key)
        # if args:
        #     args = (eval('|'.join(args)), )
        extra_filter = []
        if 'start_price' in kwargs:
            extra_filter.append("present_price+0 >= '%s'" % kwargs['start_price'])
        if 'end_price' in kwargs:
            extra_filter.append("present_price+0 <= '%s'" % kwargs['end_price'])

        kwargs = get_perfect_filter_params(cls, **kwargs)
        # root 用户
        if request.user.is_root_user:
            if extra_filter:
                instances = cls.objects.filter(**kwargs).extra(where=extra_filter)
            else:
                instances = cls.objects.filter(**kwargs)
            if isinstance(instances, Exception):
                return instances
            return [ins.perfect_detail for ins in instances]
        # 品牌用户
        elif request.user.is_brand_user:
            kwargs['business_user_id'] = request.user.id

            if extra_filter:
                instances = cls.objects.filter(**kwargs).extra(where=extra_filter)
            else:
                instances = cls.objects.filter(**kwargs)
            if isinstance(instances, Exception):
                return instances
            return [ins.perfect_detail for ins in instances]
        # 门店用户
        else:
            store_filter_fields = ('present_price', 'is_active', 'is_new', 'is_hot_sale',
                                   'is_discount', 'does_display_mirror', 'does_display_wechat')
            # 获取门店商品数据
            _kwargs = {'business_user_id': request.user.id}
            _kwargs.update(**kwargs)
            _kwargs = get_perfect_filter_params(StoresClothes, **_kwargs)
            if extra_filter:
                store_instances = StoresClothes.objects.filter(**_kwargs).extra(where=extra_filter)
            else:
                store_instances = StoresClothes.objects.filter(**_kwargs)
            if isinstance(store_instances, Exception):
                return store_instances

            store_instance_dict = {ins.clothes_id: ins for ins in store_instances}
            for p_key in store_filter_fields:
                if p_key in kwargs:
                    kwargs.pop(p_key)
            # 获取品牌商品数据
            kwargs['id__in'] = [ins.clothes_id for ins in store_instances]
            kwargs = get_perfect_filter_params(cls, **kwargs)
            instances = cls.objects.filter(**kwargs)
            if isinstance(instances, Exception):
                return instances
            return [store_instance_dict[ins.id].perfect_detail for ins in instances
                    if ins.id in store_instance_dict]

    @classmethod
    def insert_with_batch(cls, request, insert_data):
        """
        批量添加数据
        :param insert_data: 
        :param request
        :return: 
        """
        inserted_list = []
        _error = None
        for init_data in insert_data:
            init_data['business_user_id'] = request.user.id
            try:
                instance = cls(**init_data)
                instance.save()
            except Exception as e:
                _error = e.args
                break
            else:
                inserted_list.append(instance)

        if _error:
            cls.rollback(inserted_list)
            return False, _error
        return True, None

    @classmethod
    def rollback(cls, inserted_data):
        """
        回滚
        :param inserted_data: 
        :return: 
        """
        _error = None
        for ins in inserted_data:
            ins.status = ins.id + 1
            try:
                ins.save()
            except Exception as e:
                _error = e.args
        return True

    @classmethod
    def get_recommend_category_list(cls, request):
        """
        获取推荐类别列表
        :param request: 
        :return: 
        """
        # kwargs = {
        #     'is_active': 1,
        # }
        details = cls.filter_details(request)
        if isinstance(details, Exception):
            return details

        category_dict = {}
        for item in details:
            count = category_dict.get(item['category'], 0) + 1
            category_dict[item['category']] = count

        category_list = [{'category': key,
                          'count': category_dict[key]}
                         for key in category_dict]
        category_list = sorted(category_list, key=lambda x: x['count'], reverse=True)[:10]
        category_list = [item['category'] for item in category_list]
        return category_list

    @classmethod
    def get_clothes_number(cls, request):
        """
        获取上架、下架及全部商品的数量
        :param request: 
        :return: 
        """
        return_data = {'all': 0,
                       'active': 0,
                       'inactive': 0,
                       'new': 0,
                       'not_new': 0,
                       'hot_sale': 0,
                       'not_hot_sale': 0,
                       }
        kwargs = {
            'business_user_id': request.user.id
        }
        details = cls.filter_objects(**kwargs)
        for instance in details:
            if instance.is_active:
                return_data['active'] += 1
            else:
                return_data['inactive'] += 1
            if instance.is_new:
                return_data['new'] += 1
            else:
                return_data['not_new'] += 1
            if instance.is_hot_sale:
                return_data['hot_sale'] += 1
            else:
                return_data['not_hot_sale'] += 1

            return_data['all'] += 1

        return return_data

    @classmethod
    def does_all_ids_exist(cls, request, ids):
        """
        判断id列表中的元素是否存在
        如果全部存在，返回True, 
                否则返回False
        :param ids: 
        :param request: 
        :return: 
        """
        kwargs = {'id__in': list(ids)}
        # 品牌用户
        if request.user.is_brand_user:
            instances = cls.filter_objects(translate_cos_url=False, **kwargs)
            instance_ids = [ins.id for ins in instances]
            return set(ids) == set(instance_ids)
        # 门店用户（高级和普通）
        else:
            instances = StoresClothes.filter_objects(translate_cos_url=False, **kwargs)
            instance_ids = [ins.id for ins in instances]
            return set(ids) == set(instance_ids)

    @classmethod
    def batch_update(cls, request, instance_ids, validated_data):
        instances = []
        # 品牌用户
        if request.user.is_brand_user:
            with transaction.atomic():
                for instance_id in instance_ids:
                    _instance = cls.objects.select_for_update().get(pk=instance_id)
                    for attr in validated_data:
                        setattr(_instance, attr, validated_data[attr])
                    _instance.save()
                    instances.append(_instance)
        # 门店用户（高级和普通）
        else:
            with transaction.atomic():
                for instance_id in instance_ids:
                    _instance = StoresClothes.objects.select_for_update().get(pk=instance_id)
                    for attr in validated_data:
                        setattr(_instance, attr, validated_data[attr])
                    _instance.save()
                    instances.append(_instance)
        return instances

    @classmethod
    def batch_update_image(cls, request, update_image_data):
        """
        批量上传图片
        :param request: 
        :param update_image_data: {'goods_id': {'picture_order_list': [...], 'picture1_url': 'xxx', ...}}
        :return: 
        """
        instances = []
        # 添加事务
        with transaction.atomic():
            for goods_id, validated_data in update_image_data.items():
                _kwargs = {'business_user_id': request.user.id,
                           'goods_id': goods_id}
                _instance = cls.objects.select_for_update().get(**_kwargs)
                for attr in validated_data:
                    setattr(_instance, attr, validated_data[attr])
                _instance.save()
                instances.append(_instance)
        return instances


class StoresClothes(BaseModelMixin, models.Model):
    """
    门店商品数据
    """
    clothes_id = models.IntegerField(u'所属品牌商品ID')
    business_user_id = models.IntegerField(u'门店商户ID', db_index=True)

    goods_id = models.CharField(u'商品ID/货号', max_length=64)
    # original_price = models.CharField(u'原价', max_length=11)
    present_price = models.CharField(u'现价', max_length=11)
    # 商品上架、下架状态  0：下架 1：上架
    is_active = models.SmallIntegerField(u'上架/下架状态', default=1)
    # 商品是否是新品     0：否   1：是
    is_new = models.SmallIntegerField(u'是否是新品', default=1)
    # 商品是否是热销商品  0：否   1：是
    is_hot_sale = models.SmallIntegerField(u'是否是热销商品', default=1)
    # 是否打折   0: 否 1：是
    is_discount = models.SmallIntegerField(u'是否打折促销', default=0)
    # 数据状态：1：正常 其他值：已删除
    status = models.IntegerField(u'数据状态', default=1)

    does_display_mirror = models.CharField(u'是否终端展示',
                                           max_length=64,
                                           default='{"new": 0, "discount": 0, "hot_sale": 0}')
    # 小程序端展示  0：不展示  1：展示
    does_display_wechat = models.SmallIntegerField(u'小程序端是否展示', default=1)

    created = models.DateTimeField(u'创建时间', default=now)
    updated = models.DateTimeField(u'最后更新时间', auto_now=True)

    objects = BaseManager()

    class Meta:
        db_table = 'fm_store_clothes'
        unique_together = ('business_user_id', 'goods_id', 'status')
        ordering = ('-created',)

    class FMMeta:
        q_fuzzy_fields = ('title', 'goods_id')
        fuzzy_fields = ('title', )
        json_fields = ('does_display_mirror', )

    def __unicode__(self):
        return self.goods_id

    @property
    def perfect_detail(self):
        detail = super(StoresClothes, self).perfect_detail
        for key in list(detail.keys()):
            if key in self.FMMeta.json_fields:
                if detail[key]:
                    detail[key] = json.loads(detail[key])
                else:
                    if key == 'does_display_mirror':
                        detail[key] = {}
                    else:
                        detail[key] = []

        clothes_instance = Clothes.get_object(id=self.clothes_id)
        perfect_detail = clothes_instance.perfect_detail
        perfect_detail.update(**detail)
        return perfect_detail

    @classmethod
    def claim_clothes_for_store(cls, request, goods_ids):
        """
        门店认领商品
        :param request: http请求request
        :param goods_ids: 商品货号列表 如：[{'goods_id': 'HSOP39Q8GE0821'}, {'goods_id': '3293j2134kd2211'}]
        :return: 
        """
        goods_ids = [item['goods_id'] for item in goods_ids]
        bind_instance = BusinessUserBind.get_object(business_user_id=request.user.id)

        kwargs = {'goods_id__in': goods_ids,
                  'business_user_id': bind_instance.brand_user_id}
        brand_clothes_instances = Clothes.filter_objects(**kwargs)
        if brand_clothes_instances.count() != len(goods_ids):
            return Exception('Some goods_id does not exist.')

        instances = []
        # 添加事务
        try:
            with transaction.atomic():
                instances = StoreClothesAction().bulk_create(request, brand_clothes_instances)
        except Exception as e:
            return e
        return instances


class StoreClothesAction(object):
    """
    创建门店商品数据 - create, bulk_create
    """
    model = StoresClothes

    def get_perfect_init_data(self, request, brand_clothes_instance):
        """
        :param request: http请求request
        :param brand_clothes_instance: 品牌商品对象
        :return: 
        """
        init_data = {'clothes_id': brand_clothes_instance.id,
                     'business_user_id': request.user.id,
                     'goods_id': brand_clothes_instance.goods_id,
                     'present_price': brand_clothes_instance.present_price,
                     'is_active': brand_clothes_instance.is_active,
                     'is_new': brand_clothes_instance.is_new,
                     'is_hot_sale': brand_clothes_instance.is_hot_sale,
                     'is_discount': brand_clothes_instance.is_discount,
                     'does_display_mirror': brand_clothes_instance.does_display_mirror,
                     'does_display_wechat': brand_clothes_instance.does_display_wechat
                     }
        return init_data

    def bulk_create(self, request, brand_clothes_instances):
        """
        批量创建
        :param request: 
        :param brand_clothes_instances: 
        :return: 
        """
        queryset_list = []
        for ins in brand_clothes_instances:
            init_data = self.get_perfect_init_data(request, ins)
            queryset_list.append(self.model(**init_data))
        return self.model.objects.bulk_create(queryset_list)

    def create(self, request, brand_clothes_instance):
        """
        创建
        :param request: 
        :param brand_clothes_instance: 
        :return: 
        """
        init_data = self.get_perfect_init_data(request, brand_clothes_instance)
        ins = self.model(**init_data)
        return ins.save()

    def bulk_update(self, instances, validated_data):
        """
        批量修改
        :param instances: model queryset
        :param validated_data: 更新数据
        :return: 
        """
        # 添加事务
        try:
            with transaction.atomic():
                instances = instances.update(**validated_data)
        except Exception as e:
            return e
        return instances


class AdvertisingCopy(BaseModelMixin, models.Model):
    """
    镜子广告文案
    """
    business_user_id = models.IntegerField('商户用户ID', db_index=True)
    word = models.CharField('广告语', max_length=256)
    # 是否终端展示  0: 不展示  1：展示
    does_display_mirror = models.SmallIntegerField('是否终端展示', default=0)
    # 数据状态 1： 正常 非1：已删除
    status = models.IntegerField('数据状态', default=1)
    created = models.DateTimeField('创建时间', default=now)
    updated = models.DateTimeField('更新时间', auto_now=True)

    objects = BaseManager()

    class Meta:
        db_table = 'fm_advertising_copy'
        # unique_together = ('business_user_id', 'status')

    def __unicode__(self):
        return self.business_user_id


class ClothesLargeClassify(BaseModelMixin, models.Model):
    """
    服装分类（大分类）
    """
    classify_code = models.CharField('大分类代码', max_length=11, unique=True)
    classify_name = models.CharField('大分类名称', max_length=64, unique=True)
    created = models.DateTimeField('创建时间', default=now)
    updated = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'fm_clothes_large_classify'

    def __unicode__(self):
        return self.classify_code


class ClothesMiddleClassify(BaseModelMixin, models.Model):
    """
    服装分类（中分类）
    """
    large_classify_id = models.IntegerField('所属大分类', db_index=True)
    classify_code = models.CharField('中分类代码', max_length=11)
    classify_name = models.CharField('中分类名称', max_length=64)
    created = models.DateTimeField('创建时间', default=now)
    updated = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'fm_clothes_middle_classify'
        unique_together = ('classify_code', 'classify_name')

    def __unicode__(self):
        return self.classify_code

    @classmethod
    def get_detail(cls, *args, **kwargs):
        detail = super(ClothesMiddleClassify, cls).get_detail(*args, **kwargs)
        if isinstance(detail, Exception):
            return detail

        _kwargs = {'pk': detail['large_classify_id']}
        large_classify = ClothesLargeClassify.get_object(**_kwargs)
        detail['large_classify_code'] = large_classify.classify_code
        detail['large_classify_name'] = large_classify.classify_name
        return detail


class BatchUploadFileTemplate(BaseModelMixin, models.Model):
    """
    批量上传文件模板
    """
    file_url = models.CharField('文件访问路径', max_length=200)
    format = models.CharField('模板格式', max_length=20, default='csv')
    name = models.CharField('模板名称', max_length=64)

    # 数据状态 1： 正常 非1：已删除
    status = models.IntegerField('数据状态', default=1)
    created = models.DateTimeField('创建时间', default=now)
    updated = models.DateTimeField('更新时间', auto_now=True)

    objects = BaseManager()

    class Meta:
        db_table = 'fm_batch_upload_file_template'
        unique_together = ('format', 'name', 'status')

    def __unicode__(self):
        return self.file_url


class ExportFileRecord(BaseModelMixin, models.Model):
    """
    导出文件记录
    """
    file_url = models.CharField('文件访问路径', max_length=200)
    created = models.DateTimeField('创建时间', default=now)
    updated = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'fm_export_file_record'

    def __unicode__(self):
        return self.file_url
