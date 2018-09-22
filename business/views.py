# -*- coding: utf8 -*-
from django.utils.timezone import now

from business.serializers import (CookieSerializer)
from business.forms import (TTLoginForPhoneForm,)
from horizon.views import (FMActionAPIView,
                           FMDetailAPIView,
                           FMListAPIView)
from horizon import main

import json
import random


class TTLoginForPhoneAction(FMActionAPIView):
    """
    TT登录
    """
    post_form_class = TTLoginForPhoneForm
    post_serializer_class = CookieSerializer
    model_class = None

    def post(self, request, *args, **kwargs):
        """
        TT登录
        :param request: 
        :param args: 
        :param kwargs: 
        :return: 
        """
        return super(TTLoginForPhoneAction, self).post(request, *args, **kwargs)


