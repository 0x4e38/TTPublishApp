# -*- coding:utf8 -*-
from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns
from users import views as users_view

app_name = 'users'
urlpatterns = [
    url(r'^login/$', users_view.AuthLogin.as_view()),
    url(r'^logout/$', users_view.AuthLogout.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)


