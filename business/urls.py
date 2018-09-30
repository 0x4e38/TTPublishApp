# -*- coding:utf8 -*-
from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from business import views

app_name = 'business'
urlpatterns = [
    url(r'^tt_login/$', views.TTLoginAction.as_view()),
    url(r'^tt_comment/$', views.TTCommentAction.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)


