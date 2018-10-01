# -*- encoding: utf-8 -*-
from horizon import forms


class TTLoginActionForm(forms.Form):
    """
    TT登录
    """
    login_type = forms.ChoiceField(choices=(('phone_identifying_code', 1),
                                            ('phone_password', 2),
                                            ('email_password', 3)),
                                   error_messages={
                                       'invalid_choice': 'Params [login_type] must in ["phone_identifying_code", '
                                                         '"phone_password", "email_password"]',
                                       'required': 'Params [login_type] must in ["phone_identifying_code", '
                                                         '"phone_password", "email_password"]',
                                   })
    phone = forms.CharField(min_length=11, max_length=11,
                            error_messages={
                                'min_length': u'手机号位数不够',
                                'max_length': u'手机号位数超限（不是一个手机号）',
                               },
                            required=False)
    email = forms.EmailField(required=False)
    password = forms.CharField(min_length=4,
                               error_messages={
                                   'min_length': u'密码或验证码最少为4位'
                               })


class TTCommentActionForm(forms.Form):
    """
    TT评论
    """
    tt_user_id = forms.IntegerField(min_value=1)
    article_url = forms.CharField(min_length=32,
                                  error_messages={
                                      'required': u'文章url不能为空',
                                  })
    content = forms.CharField(min_length=1, max_length=256,
                              error_messages={
                                  'required': u'评论内容不能为空',
                                  'max_length': u'评论内容太长',
                              })


class TTSignedUserListForm(forms.Form):
    """
    TT登录用户列表
    """
    page_size = forms.IntegerField(min_value=1, required=False)
    page_index = forms.IntegerField(min_value=1, required=False)


class ArticleInputForm(forms.Form):
    url = forms.CharField(max_length=128)
    title = forms.CharField(max_length=256, required=False)


class ArticleUpdateForm(forms.Form):
    pk = forms.IntegerField(min_value=1)
    url = forms.CharField(max_length=128, required=False)
    title = forms.CharField(max_length=256, required=False)


class ArticleDeleteForm(forms.Form):
    pk = forms.IntegerField(min_value=1)


class ArticleDetailForm(forms.Form):
    pk = forms.IntegerField(min_value=1)


class ArticleListForm(forms.Form):
    page_size = forms.IntegerField(min_value=1, required=False)
    page_index = forms.IntegerField(min_value=1, required=False)


class ArticleCommentRecrodListForm(forms.Form):
    page_size = forms.IntegerField(min_value=1, required=False)
    page_index = forms.IntegerField(min_value=1, required=False)

