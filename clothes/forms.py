# -*- encoding: utf-8 -*-
from horizon import forms
from django import forms as django_forms


class ClothesCreateForm(forms.Form):
    title = forms.CharField(min_length=2, max_length=128)
    subtitle = forms.CharField(max_length=256, required=False)
    description = forms.CharField(max_length=512, required=False)
    goods_id = forms.CharField(min_length=1, max_length=64)
    original_price = forms.FloatField(min_value=0.01)
    present_price = forms.FloatField(min_value=0.01, required=False)
    # 推荐理由
    recommend_title = forms.CharField(max_length=32, required=False)
    # 推荐理由-详细
    recommend_subtitle = forms.CharField(max_length=64, required=False)
    # 服装适合性别：1：男装 2：女装  3：中性
    gender = forms.ChoiceField(choices=((1, 1),
                                        (2, 2),
                                        (3, 3)),
                               error_messages={
                                   'required': u'gender must in [1, 2, 3]',
                               })
    # # 服装适合人群 1：成人 2：儿童
    # crowd = forms.ChoiceField(choices=((1, 1),
    #                                    (2, 2)),
    #                           error_messages={
    #                               'required': u'crowd must in [1, 2]',
    #                           },
    #                           required=False)
    # # 服装类别：例如（裙子，短袖、长裤等）
    # category = forms.CharField(max_length=64)
    # 服装适合体型：A1：瘦  A2：匀称  A3：胖
    #            B1：瘦  B2：匀称  B3：胖
    #            C1：瘦  C2：匀称  C3：胖
    # 字段值：JSON字符串，如：'["A1", "B2", "C3"]'
    shape = forms.CharField(max_length=64, required=False)
    # # 尺寸
    # size = forms.CharField(max_length=11)
    # 商品上架、下架状态
    is_active = forms.ChoiceField(choices=((0, 1),
                                           (1, 2)),
                                  required=False)
    # 商品是否是新品
    is_new = forms.ChoiceField(choices=((0, 1),
                                        (1, 2)),
                               required=False)
    # 商品是否是热销商品
    is_hot_sale = forms.ChoiceField(choices=((0, 1),
                                             (1, 2)),
                                    required=False)
    # 是否打折   0: 否 1：是
    is_discount = forms.ChoiceField(choices=((0, 1),
                                             (1, 2)),
                                    required=False)
    video = forms.FileField(required=False)
    picture1 = forms.FileField(required=False)
    picture2 = forms.FileField(required=False)
    picture3 = forms.FileField(required=False)
    picture4 = forms.FileField(required=False)
    # 标签  如：显瘦 百搭 基本款
    # 字段值：JSON字符串，如：'["显瘦", "百搭", "基本款"]'
    tags = forms.CharField(max_length=256, required=False)
    # 颜色：如：绿色，白色，黑色
    color = forms.CharField(max_length=32)
    # 所属中分类ID
    classify_id = forms.IntegerField(min_value=1)
    # 是否终端展示
    # 字段值：JSON字符串，如：'{"new": 0,
    #                       "discount": 1,
    #                       "hot_sale": 1}'
    does_display_mirror = forms.CharField(required=False)
    # 小程序端展示  0：不展示  1：展示
    does_display_wechat = forms.ChoiceField(choices=((0, 1),
                                                     (1, 2)),
                                            required=False)
    # 商品属性
    fabric_component = forms.CharField(max_length=64, required=False)
    stereotype = forms.CharField(max_length=48, required=False)
    thickness = forms.CharField(max_length=32, required=False)
    elastic = forms.CharField(max_length=48, required=False)


class ClothesUpdateForm(forms.Form):
    pk = forms.IntegerField(min_value=1)
    title = forms.CharField(min_length=2, max_length=128, required=False)
    subtitle = forms.CharField(max_length=256, required=False)
    description = forms.CharField(max_length=512, required=False)
    goods_id = forms.CharField(min_length=1, max_length=64, required=False)
    original_price = forms.FloatField(min_value=0.01, required=False)
    present_price = forms.FloatField(min_value=0.01, required=False)
    # 推荐理由
    recommend_title = forms.CharField(max_length=32, required=False)
    # 推荐理由-详细
    recommend_subtitle = forms.CharField(max_length=64, required=False)
    # 服装适合性别：1：男装 2：女装  3：中性
    gender = forms.ChoiceField(choices=((1, 1),
                                        (2, 2),
                                        (3, 3)),
                               error_messages={
                                   'required': u'gender must in [1, 2, 3]',
                               },
                               required=False)
    # # 服装适合人群 1：成人 2：儿童
    # crowd = forms.ChoiceField(choices=((1, 1),
    #                                    (2, 2)),
    #                           error_messages={
    #                               'required': u'crowd must in [1, 2]',
    #                           },
    #                           required=False)
    # # 服装类别：例如（裙子，短袖、长裤等）
    # category = forms.CharField(max_length=64, required=False)
    # 服装适合体型：A1：瘦  A2：匀称  A3：胖
    #            B1：瘦  B2：匀称  B3：胖
    #            C1：瘦  C2：匀称  C3：胖
    # 字段值：JSON字符串，如：'["A1", "B2", "C3"]'
    shape = forms.CharField(max_length=64, required=False)
    # # 尺寸
    # size = forms.CharField(max_length=11, required=False)
    # 商品上架、下架状态
    is_active = forms.ChoiceField(choices=((0, 1),
                                           (1, 2)),
                                  required=False)
    # 商品是否是新品
    is_new = forms.ChoiceField(choices=((0, 1),
                                        (1, 2)),
                               required=False)
    # 商品是否是热销商品
    is_hot_sale = forms.ChoiceField(choices=((0, 1),
                                             (1, 2)),
                                    required=False)
    # 是否打折   0: 否 1：是
    is_discount = forms.ChoiceField(choices=((0, 1),
                                             (1, 2)),
                                    required=False)
    video = forms.FileField(required=False)
    picture1 = forms.FileField(required=False)
    picture2 = forms.FileField(required=False)
    picture3 = forms.FileField(required=False)
    picture4 = forms.FileField(required=False)
    # 图片保存顺序：JSON字符串，形如：
    #  '["picture1", "picture2", "picture3", "picture4"]'
    picture_order_list = forms.CharField(max_length=128, required=False)
    # 视频读取、存储顺序，字段类型：JSON字符串：形如：
    #            '["video"]'
    video_order_list = forms.CharField(max_length=128, required=False)
    # 标签  如：1：显瘦 2：百搭 3：基本款
    # 字段值：JSON字符串，如：'["显瘦", "百搭", "基本款"]'
    tags = forms.CharField(max_length=256, required=False)
    color = forms.CharField(max_length=32, required=False)
    # 所属中分类ID
    classify_id = forms.IntegerField(min_value=1, required=False)
    # 是否终端展示
    # 字段值：JSON字符串，如：'{"new": 0,
    #                       "discount": 1,
    #                       "hot_sale": 1}'
    does_display_mirror = forms.CharField(required=False)
    # 小程序端展示  0：不展示  1：展示
    does_display_wechat = forms.ChoiceField(choices=((0, 1),
                                                     (1, 2)),
                                            required=False)
    # 商品属性
    fabric_component = forms.CharField(max_length=64, required=False)
    stereotype = forms.CharField(max_length=48, required=False)
    thickness = forms.CharField(max_length=32, required=False)
    elastic = forms.CharField(max_length=48, required=False)
    # 衣服颜色（智能匹配使用）
    clothes_color_id = forms.IntegerField(min_value=1, required=False)
    # 衣服风格（智能匹配使用）
    clothes_style_id = forms.IntegerField(min_value=1, required=False)


class ClothesBatchCreateColumnDetailForm(forms.Form):
    main_sku_code = forms.CharField(min_length=10, max_length=32)
    title = forms.CharField(min_length=2, max_length=128)
    goods_id = forms.CharField(min_length=1, max_length=64)
    original_price = forms.FloatField(min_value=0.01)
    present_price = forms.FloatField(min_value=0.01)
    # 服装适合性别：1：男装 2：女装  3：中性
    gender = forms.ChoiceField(choices=((1, 1),
                                        (2, 2),
                                        (3, 3)),
                               error_messages={
                                   'required': u'gender must in [1, 2, 3]',
                               })
    # 颜色：如：绿色，白色，黑色
    color = forms.CharField(max_length=32)
    # 所属中分类ID
    classify_id = forms.IntegerField(min_value=1)
    # 商品上架、下架状态
    is_active = forms.ChoiceField(choices=((0, 1),
                                           (1, 2)),
                                  required=False)
    # 商品是否是新品
    is_new = forms.ChoiceField(choices=((0, 1),
                                        (1, 2)),
                               required=False)
    # 商品是否是热销商品
    is_hot_sale = forms.ChoiceField(choices=((0, 1),
                                             (1, 2)),
                                    required=False)
    # 是否打折   0: 否 1：是
    is_discount = forms.ChoiceField(choices=((0, 1),
                                             (1, 2)),
                                    required=False)
    description = forms.CharField(max_length=512, required=False)
    # 字段值：JSON字符串，如：'["显瘦", "百搭", "基本款"]'
    tags = forms.CharField(max_length=256, required=False)
    # 商品属性
    fabric_component = forms.CharField(max_length=64, required=False)
    stereotype = forms.CharField(max_length=48, required=False)
    thickness = forms.CharField(max_length=32, required=False)
    elastic = forms.CharField(max_length=48, required=False)
    # 推荐理由
    recommend_title = forms.CharField(max_length=32, required=False)
    # 推荐理由-详细
    recommend_subtitle = forms.CharField(max_length=64, required=False)


class ClothesDeleteForm(forms.Form):
    pk = forms.IntegerField()


class ClothesDetailForm(forms.Form):
    pk = forms.IntegerField()


class ClothesListForm(forms.Form):
    title = forms.CharField(max_length=128, required=False)
    business_user_id = forms.IntegerField(min_value=1, required=False)
    goods_id = forms.CharField(max_length=64, required=False)
    main_sku_code = forms.CharField(max_length=32, required=False)
    # 服装适合性别：1：男装 2：女装  3：中性
    gender = forms.ChoiceField(choices=((1, 1),
                                        (2, 2),
                                        (3, 3)),
                               error_messages={
                                   'required': u'gender must in [1, 2, 3]',
                               },
                               required=False)
    # 大分类
    large_classify_id = forms.IntegerField(min_value=1, required=False)
    # 中分类
    middle_classify_id = forms.IntegerField(min_value=1, required=False)
    # 是否打折   0: 否 1：是
    is_discount = forms.ChoiceField(choices=((0, 1),
                                             (1, 2)),
                                    required=False)
    # 商品是否是新品
    is_new = forms.ChoiceField(choices=((0, 1),
                                        (1, 2)),
                               required=False)
    # 是否是热卖
    is_hot_sale = forms.ChoiceField(choices=((0, 1),
                                             (1, 2)),
                                    required=False)
    # 商品上架、下架状态
    is_active = forms.ChoiceField(choices=((0, 1),
                                           (1, 2)),
                                  required=False)
    # 价格区间 start_price和end_price
    start_price = forms.CharField(max_length=12, required=False)
    end_price = forms.CharField(max_length=12, required=False)
    # 颜色
    color = forms.CharField(max_length=32, required=False)

    # keyword = forms.CharField(max_length=128, required=False)
    # category = forms.CharField(max_length=64, required=False)
    # recommend_type = forms.ChoiceField(choices=(('active', 1),
    #                                             ('inactive', 2),
    #                                             ('hot_sale', 3),
    #                                             ('not_hot_sale', 4),
    #                                             ('new', 5),
    #                                             ('not_new', 6)),
    #                                    required=False)
    # active_type = forms.ChoiceField(choices=(('all', 1),
    #                                          ('active', 2),
    #                                          ('inactive', 3),
    #                                          ('hot_sale', 4),
    #                                          ('not_hot_sale', 5),
    #                                          ('new', 6),
    #                                          ('not_new', 7)
    #                                          ),
    #                                 required=False)
    page_size = forms.IntegerField(required=False)
    page_index = forms.IntegerField(required=False)


class ClothesBatchCreateForm(forms.Form):
    # 文件格式：excel，字段顺序：
    # 商品名称（title），货号（goods_id），原价（original_price），现价（present_price），男装/女装（gender），
    # 服装类别（category），适合体型（shape）：多个值用逗号分隔，推荐理由（recommend_title）
    upload_file = forms.FileField()


class ClothesNumberDetailForm(forms.Form):
    pass


class ClothesBatchUpdateForm(forms.Form):
    # 待更新数据的ID，JSON字符串格式
    # 形如：'[1, 2, 3, 4]'
    update_ids = forms.CharField(max_length=1280)
    action = forms.ChoiceField(choices=(('active', 1),
                                        ('inactive', 2),
                                        ('hot_sale', 3),
                                        ('not_hot_sale', 4),
                                        ('new', 5),
                                        ('not_new', 6),
                                        ('discount', 7),
                                        ('not_discount', 8)),
                               error_messages={
                                   'required': 'Params [action] must in '
                                               '["active", "inactive", "hot_sale", "not_hot_sale", '
                                               '"new", "not_new", "discount", "not_discount"]'
                               })


class AdvertisingCopyCreateForm(forms.Form):
    word = forms.CharField(min_length=1, max_length=255)


class AdvertisingCopyUpdateForm(forms.Form):
    pk = forms.IntegerField(min_value=1)
    word = forms.CharField(min_length=1, max_length=255, required=False)
    # 是否终端展示  0: 不展示  1：展示
    does_display_mirror = forms.ChoiceField(choices=((0, 1),
                                                     (1, 2)),
                                            required=False)


class AdvertisingCopyDeleteForm(forms.Form):
    pk = forms.IntegerField(min_value=1)


class AdvertisingCopyDetailForm(forms.Form):
    pk = forms.IntegerField(min_value=1)


class AdvertisingCopyListForm(forms.Form):
    # 是否终端展示  0: 不展示  1：展示
    does_display_mirror = forms.ChoiceField(choices=((0, 1),
                                                     (1, 2)),
                                            required=False)
    page_size = forms.IntegerField(required=False)
    page_index = forms.IntegerField(required=False)


class ClothesLargeClassifyListForm(forms.Form):
    page_size = forms.IntegerField(required=False)
    page_index = forms.IntegerField(required=False)


class ClothesMiddleClassifyListForm(forms.Form):
    large_classify_id = forms.IntegerField(required=False)
    page_size = forms.IntegerField(required=False)
    page_index = forms.IntegerField(required=False)


class BatchUploadFileTemplateForm(forms.Form):
    name = forms.ChoiceField(choices=(('clothes', 1),
                                      ('claim_clothes', 2),
                                      ('store', 3)),
                             error_messages={
                                 'required': 'Params [name] must in ["clothes", "claim_clothes", "store"]'
                             })
    format = forms.ChoiceField(choices=(('csv', 1),
                                        ('xls', 2)),
                               error_messages={
                                   'required': 'Params [format] must in ["csv", "xls"]'
                               })


class StoreListForm(forms.Form):
    pass


class MirrorClothesManageListForm(forms.Form):
    # 类型：折扣系列: discount   最新搭配: new
    type = forms.ChoiceField(choices=(('discount', 1),
                                      ('new', 2)),
                             error_messages={
                                 'required': 'Params [type] must in ["discount", "new"]'
                             })
    page_size = forms.IntegerField(required=False)
    page_index = forms.IntegerField(required=False)


class MirrorClothesManageActionForm(forms.Form):
    pk = forms.IntegerField(min_value=1)
    # 类型：折扣系列: discount   最新搭配: new
    type = forms.ChoiceField(choices=(('discount', 1),
                                      ('new', 2)),
                             error_messages={
                                 'required': 'Params [type] must in ["discount", "new"]'
                             })
    status = forms.ChoiceField(choices=((0, 1),
                                        (1, 2)))


class ExportFileActionForm(ClothesListForm):
    # 导出类型：选择部分（导出选择部分）：select   全部（导出全部）：all
    type = forms.ChoiceField(choices=(('select', 1),
                                      ('screen', 2),
                                      ('all', 3),),
                             error_messages={
                                 'required': 'Params [type] must in ["select", "screen", "all"]'
                             })
    # 导出数据的ID
    # 字段值：JSON字符串，如：'[1, 2, 3]'
    ids = forms.CharField(required=False)


class BatchUploadImageForm(forms.Form):
    compressed_file = forms.FileField()


class BatchClaimClothesActionForm(forms.Form):
    """
    门店批量认领商品 
    """
    claim_file = forms.FileField()


class BatchClaimClothesColumnDetailForm(forms.Form):
    """
    门店批量认领商品--验证
    """
    goods_id = forms.CharField(max_length=64)


class ClothesColorListForm(forms.Form):
    """
    衣服颜色列表
    """
    pass


class ClothesStyleListForm(forms.Form):
    """
    服装风格列表
    """
    pass

