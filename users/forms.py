# -*- encoding: utf-8 -*-
from horizon import forms


class PhoneForm(forms.Form):
    phone = forms.CharField(max_length=20, min_length=11,
                            error_messages={
                                   'required': u'手机号不能为空',
                                   'min_length': u'手机号位数不够'
                               })


class PasswordForm(forms.Form):
    password = forms.CharField(min_length=6,
                               max_length=50,
                               error_messages={
                                   'required': u'密码不能为空',
                                   'min_length': u'密码长度不能少于6位'
                               })
    # confirm_password = forms.CharField(min_length=6,
    #                                    max_length=50,
    #                                    error_messages={
    #                                        'required': u'密码不能为空',
    #                                        'min_length': u'密码长度不能少于6位'
    #                                    })


class SendIdentifyingCodeForm(PhoneForm):
    """
    发送手机验证码（未登录状态）
    """
    pass


class VerifyIdentifyingCodeForm(PhoneForm):
    """
    验证手机验证码
    """
    identifying_code = forms.CharField(min_length=6, max_length=10,
                                       error_messages={
                                           'required': u'验证码不能为空'
                                       })


class BrandListForm(forms.Form):
    page_size = forms.IntegerField(min_value=1, required=False)
    page_index = forms.IntegerField(min_value=1, required=False)


class UpdateUserInfoForm(forms.Form):
    """
    更改用户信息
    """
    password = forms.CharField(min_length=6, max_length=50, required=False)
    nickname = forms.CharField(max_length=100, required=False)
    gender = forms.IntegerField(min_value=1, max_value=2, required=False)
    birthday = forms.DateField(required=False)
    province = forms.CharField(max_length=16, required=False)
    city = forms.CharField(max_length=32, required=False)
    head_picture = forms.ImageField(required=False)


class CreateUserForm(VerifyIdentifyingCodeForm, PasswordForm):
    """
    用户注册
    """


class SetPasswordForm(CreateUserForm):
    """
    忘记密码
    """


class WXAuthCreateUserForm(VerifyIdentifyingCodeForm):
    """
    微信授权登录后绑定用户手机号
    """
    # out_open_id = forms.CharField(max_length=64)


class AdvertListForm(forms.Form):
    food_court_id = forms.IntegerField(min_value=1)
    ad_position_name = forms.CharField(max_length=20, required=False)


class WXAuthLoginForm(forms.Form):
    callback_url = forms.CharField(max_length=256, required=False)


class BatchUploadStoreForm(forms.Form):
    store_file = forms.FileField()


class BusinessUserBatchCreateColumnDetailForm(forms.Form):
    phone = forms.CharField(min_length=11, max_length=20)
    city_id = forms.IntegerField(min_value=1)
    address = forms.CharField(max_length=256)
    brand = forms.CharField(max_length=64)
    permission_group_id = forms.IntegerField(min_value=1)
    business_name = forms.CharField(max_length=128)
    manager = forms.CharField(max_length=20)
    email = forms.EmailField(max_length=64, required=False)
    backup_phone = forms.CharField(min_length=11, max_length=20)
    hotline = forms.CharField(min_length=7, max_length=20)
    # role = forms.CharField(max_length=32)


class BatchUploadStoreFileTemplateForm(forms.Form):
    format = forms.ChoiceField(choices=(('csv', 1),
                                        ('xls', 2)),
                               error_messages={
                                   'required': 'Params [format] must in ["csv", "xls"]'
                               })


class CreateStoreUserForm(forms.Form):
    phone = forms.CharField(min_length=11, max_length=20)
    city_id = forms.IntegerField(min_value=1)
    address = forms.CharField(max_length=256)
    permission_group_id = forms.IntegerField(min_value=1)
    business_name = forms.CharField(max_length=128)
    manager = forms.CharField(max_length=20)
    email = forms.EmailField(max_length=64, required=False)
    backup_phone = forms.CharField(min_length=11, max_length=20)
    hotline = forms.CharField(min_length=7, max_length=20)


class UpdateStoreUserForm(forms.Form):
    pk = forms.IntegerField(min_value=1)
    phone = forms.CharField(min_length=11, max_length=20, required=False)
    city_id = forms.IntegerField(min_value=1, required=False)
    address = forms.CharField(max_length=256, required=False)
    permission_group_id = forms.IntegerField(min_value=1, required=False)
    business_name = forms.CharField(max_length=128, required=False)
    manager = forms.CharField(max_length=20, required=False)
    email = forms.EmailField(max_length=64, required=False)
    backup_phone = forms.CharField(min_length=11, max_length=20, required=False)
    hotline = forms.CharField(min_length=7, max_length=20, required=False)


class StoreDetailForm(forms.Form):
    pk = forms.IntegerField(min_value=1)


class StoreListForm(forms.Form):
    business_name = forms.CharField(max_length=128, required=False)
    permission_group = forms.ChoiceField(choices=(('store_senior', 1),
                                                  ('store_common', 2)),
                                         error_messages={
                                             'required': 'Params [permission_group]'
                                                         ' must in ["store_senior", "store_common"]'
                                         },
                                         required=False)
    province_id = forms.IntegerField(min_value=1, required=False)
    city_id = forms.IntegerField(min_value=1, required=False)
    page_size = forms.IntegerField(min_value=1, required=False)
    page_index = forms.IntegerField(min_value=1, required=False)


class AreaProvinceListForm(forms.Form):
    page_size = forms.IntegerField(min_value=1, required=False)
    page_index = forms.IntegerField(min_value=1, required=False)


class AreaCityListForm(forms.Form):
    province_id = forms.IntegerField(min_value=1, required=False)
    page_size = forms.IntegerField(min_value=1, required=False)
    page_index = forms.IntegerField(min_value=1, required=False)

