# -*- coding:utf8 -*-
from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from business import views

app_name = 'business'
urlpatterns = [
    url(r'^business_statistical_detail/$', views.BusinessStatisticalDetail.as_view()),
    url(r'^clothes_try_on_number_list/$', views.ClothesTryOnNumberList.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)


