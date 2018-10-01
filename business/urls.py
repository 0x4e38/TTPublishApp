# -*- coding:utf8 -*-
from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from business import views

app_name = 'business'
urlpatterns = [
    url(r'^tt_login/$', views.TTLoginAction.as_view()),
    url(r'^tt_comment/$', views.TTCommentAction.as_view()),

    url(r'^tt_signed_user_list/$', views.TTSignedUserList.as_view()),
    url(r'^tt_article_action/$', views.ArticleAction.as_view()),
    url(r'^tt_article_detail/$', views.ArticleDetail.as_view()),
    url(r'^tt_article_list/$', views.ArticleList.as_view()),

    url(r'^tt_article_comment_record_list/$', views.ArticleCommentRecordList.as_view()),

]

urlpatterns = format_suffix_patterns(urlpatterns)


