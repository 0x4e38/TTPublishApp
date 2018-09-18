# -*- coding:utf8 -*-
from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from clothes import views

app_name = 'clothes'
urlpatterns = [
    url(r'^clothes_action/$', views.ClothesAction.as_view()),
    url(r'^clothes_detail/$', views.ClothesDetail.as_view()),
    url(r'^clothes_list/$', views.ClothesList.as_view()),

    url(r'^get_clothes_number/$', views.ClothesNumberDetail.as_view()),
    url(r'^clothes_category_list/$', views.ClothesCategoryList.as_view()),
    url(r'^clothes_batch_action/$', views.ClothesBatchAction.as_view()),

    url(r'^advertising_copy_action/$', views.AdvertisingCopyAction.as_view()),
    url(r'^advertising_copy_detail/$', views.AdvertisingCopyDetail.as_view()),
    url(r'^advertising_copy_list/$', views.AdvertisingCopyList.as_view()),

    # 大分类列表
    url(r'^clothes_large_classify_list/$', views.ClothesLargeClassifyList.as_view()),
    # 中分类列表
    url(r'^clothes_middle_classify_list/$', views.ClothesMiddleClassifyList.as_view()),

    # 批量上传文件模板下载
    url(r'^batch_upload_file_template_detail/$', views.BatchUploadFileTemplateDetail.as_view()),
    # # 门店列表
    # url(r'^store_list/$', views.StoreList.as_view()),

    # 魔镜商品管理：折扣/新品列表
    url(r'^mirror_clothes_manage_list/$', views.MirrorClothesManageList.as_view()),
    url(r'^mirror_clothes_manage_action/$', views.MirrorClothesManageAction.as_view()),

    # 批量导出数据
    url(r'export_clothes_detail/$', views.ExportFileDetail.as_view()),
    # 批量上传图片
    url(r'^batch_upload_image_action/$', views.BatchUploadImageAction.as_view()),

    # 门店认领商品（品牌导入的商品）
    url(r'^batch_claim_clothes_action/$', views.BatchClaimClothesAction.as_view()),

    # 衣服颜色列表
    url(r'^clothes_color_list/$', views.ClothesColorList.as_view()),
    # 服装风格列表
    url(r'^clothes_style_list/$', views.ClothesStyleList.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)


