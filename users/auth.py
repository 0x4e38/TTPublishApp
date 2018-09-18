# -*- coding:utf8 -*-
from users.models import BusinessUser, IdentifyingCode
from django.utils.timezone import now


class BusinessUserBackend(object):
    """
    验证用户
    """
    def authenticate(self, username=None, password=None):
        kwargs = {'phone': username}
        identifying_kwargs = {'phone': username,
                              'identifying_code': password}

        user = BusinessUser.get_object(translate_cos_url=False, **kwargs)
        if isinstance(user, Exception):
            return None

        code = IdentifyingCode.get_object(**identifying_kwargs)
        if isinstance(code, Exception):
            return None

        user.last_login = now()
        user.save()
        return user

    # def authenticate(self, username=None, password=None):
    #     try:
    #         user = BusinessUser.objects.get(phone=username, is_active=1)
    #     except BusinessUser.DoesNotExist:
    #         pass
    #     else:
    #         if user.check_password(password):
    #             user.last_login = now()
    #             user.save()
    #             return user
    #     return None

    def get_user(self, user_id):
        try:
            return BusinessUser.objects.get(pk=user_id, is_active=1)
        except BusinessUser.DoesNotExist:
            return None
