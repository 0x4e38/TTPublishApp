# -*- encoding: utf-8 -*-
from horizon import forms


class PublicParamsForm(forms.Form):
    """
    公共参数表单（每个请求都带着此类参数）
    """
    xaid = forms.CharField(min_length=1, max_length=64,
                           error_messages={
                               'required': u'设备ID不能为空',
                               'min_length': u'设备ID长度不能少于1位',
                               'max_length': u'设备ID长度不能多于64位'
                           })
    cnl = forms.CharField(min_length=1, max_length=64,
                          error_messages={
                              'required': u'渠道号不能为空',
                              'min_length': u'渠道号长度不能少于1位',
                              'max_length': u'渠道号长度不能多于64位'
                          })
    cv = forms.CharField(min_length=1, max_length=16,
                         error_messages={
                             'required': u'Android版本号不能为空'
                         })
    mcc = forms.CharField(min_length=1,
                          error_messages={
                              'required': u'mcc不能为空'
                          })
    nmcc = forms.CharField(min_length=1,
                           error_messages={
                               'required': u'nmcc不能为空'
                           })
    tstamp = forms.CharField(min_length=10,
                             error_messages={
                                 'required': u'时间戳不能为空'
                             })
