from django import forms
from django.forms import widgets


class ChoiceField(forms.ChoiceField):
    def to_python(self, value):
        for key2, value2 in self.choices:
            if key2 == value or str(key2) == value:
                if isinstance(key2, int):
                    return int(value)
                elif isinstance(key2, float):
                    return float(value)
        return value

