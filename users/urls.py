# -*- coding:utf8 -*-
from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns
from users import views as users_view

app_name = 'users'
urlpatterns = [
    url(r'^user_not_logged_action/$', users_view.UserNotLoggedAction.as_view()),
    url(r'^user_action/$', users_view.UserAction.as_view()),
    url(r'^user_detail/$', users_view.UserDetail.as_view()),
    url(r'^brand_list/$', users_view.BrandList.as_view()),

    url(r'^send_identifying_code/$', users_view.IdentifyingCodeAction.as_view()),

    url(r'^login/$', users_view.AuthLogin.as_view()),
    url(r'^logout/$', users_view.AuthLogout.as_view()),

    # 门店用户批量导入
    url(r'^batch_upload_store_user_action/$', users_view.BatchUploadStoreAction.as_view()),
    # # 获取批量上传门店信息的文件模板
    # url(r'^batch_upload_store_user_template_detail/$', users_view.BatchUploadStoreFileTemplateDetail.as_view()),
    # 新建门店用户、修改门店用户信息
    url(r'^store_user_action/$', users_view.StoreUserAction.as_view()),
    # 获取省份列表
    url(r'^province_list/$', users_view.AreaProvinceList.as_view()),
    url(r'^city_list/$', users_view.AreaCityList.as_view()),
    # 品牌所属：门店列表
    url(r'^store_list/$', users_view.StoreList.as_view()),
    # 品牌所属：门店详情
    url(r'^store_detail/$', users_view.StoreDetail.as_view()),

]

urlpatterns = format_suffix_patterns(urlpatterns)


