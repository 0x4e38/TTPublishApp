# -*- coding:utf8 -*-
"""TTPublishApp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from rest_framework import routers
# from rest_framework_swagger.views import get_swagger_view
from horizon.schema import SwaggerSchemaView

# Create our schema's view w/ the get_schema_view() helper method. Pass in the proper Renderers for swagger
# schema_view = get_swagger_view(title='Users API')

urlpatterns = [
    url(r'^docs/', SwaggerSchemaView.as_view(), name="docs"),
    # url(r'^api-auth', include('rest_framework.urls', namespace='rest_framework')),
    # url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),

    url(r'^auth/', include('users.urls', namespace='users')),
    url(r'^business/', include('business.urls', namespace='business')),

]

