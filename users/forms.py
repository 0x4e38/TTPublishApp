# -*- encoding: utf-8 -*-
from horizon import forms


class TTLoginForPhoneForm(forms.Form):
    """
    TT登录
    """
    phone = forms.CharField(min_length=11, max_length=11,
                            error_messages={
                                'required': u'手机号不能为空',
                                'min_length': u'手机号位数不够',
                                'max_length': u'手机号位数超限（不是一个手机号）',
                               })
    identifying_code = forms.CharField(min_length=4, max_length=4,
                                       error_messages={
                                           'required': u'验证码不能为空',
                                           'min_length': u'验证码只能为4位',
                                           'max_length': u'验证码只能为4位',
                                       })

