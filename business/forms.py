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
    comment_content = forms.CharField(min_length=1, max_length=256,
                                      error_messages={
                                          'required': u'评论内容不能为空',
                                          'max_length': u'评论内容太长',
                                      })

