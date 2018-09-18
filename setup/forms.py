# -*- encoding: utf-8 -*-
from horizon import forms


class ApkUploadForm(forms.Form):
    apk_file = forms.FileField()
    version = forms.IntegerField(min_value=1)


class ApkUpdateStatusForm(forms.Form):
    pk = forms.IntegerField(min_value=1)
    status = forms.ChoiceField(choices=((1, 1),
                                        (2, 2)),
                               error_messages={
                                   'required': 'Param [status] must in [1, 2]'
                               })


class ApkVersionListForm(forms.Form):
    page_size = forms.IntegerField(min_value=1, required=False)
    page_index = forms.IntegerField(min_value=1, required=False)
