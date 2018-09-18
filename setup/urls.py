# -*- coding:utf8 -*-
from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from setup import views

app_name = 'setup'
urlpatterns = [
    url(r'^upload_apk_action/$', views.ApkUploadAction.as_view()),
    url(r'^android_apk_list/$', views.ApkVersionList.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)


