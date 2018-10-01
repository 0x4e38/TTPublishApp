# -*- coding:utf8 -*-
from django.contrib.auth.models import User, Group
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from django.conf import settings

from horizon.models import model_to_dict
from horizon import main
from horizon.decorators import has_permission_to_update
from horizon.serializers import (BaseListSerializer,
                                 BaseModelSerializer,
                                 BaseSerializer,
                                 timezoneStringTostring)
from users.models import (BusinessUser,)

import urllib
import os
import json
import re
import copy


class UserSerializer(BaseModelSerializer):
    request = None

    def __init__(self, instance=None, data=None, request=None, **kwargs):
        if data:
            self.request = request
            data['brand'] = request.user.brand
            data['password'] = make_password(main.make_random_char_and_number_of_string())
            super(UserSerializer, self).__init__(data=data, **kwargs)
        else:
            super(UserSerializer, self).__init__(instance, **kwargs)

    class Meta:
        model = BusinessUser
        fields = ('email', 'phone', 'business_name', 'logo_url')
