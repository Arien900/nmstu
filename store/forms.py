# store/forms.py
from django import forms
from .data import STYLES, SIZES

class SettingsForm(forms.Form):
    theme = forms.ChoiceField(choices=[], required=False)
    language = forms.ChoiceField(choices=[], required=False)
    favorite_styles = forms.MultipleChoiceField(choices=[], required=False, widget=forms.CheckboxSelectMultiple)
    preferred_sizes = forms.MultipleChoiceField(choices=[], required=False, widget=forms.CheckboxSelectMultiple)

    def __init__(self, *args, **kwargs):
        lang = kwargs.pop('lang', 'ru')
        super().__init__(*args, **kwargs)

        # темы с метками зависящими от языка
        if lang == 'ru':
            self.fields['theme'].choices = [('light','Светлая'), ('dark','Тёмная')]
            self.fields['language'].choices = [('ru','Русский'), ('en','English')]
        else:
            self.fields['theme'].choices = [('light','Light'), ('dark','Dark')]
            self.fields['language'].choices = [('en','English'), ('ru','Русian')]

        # favorite_styles — метки из STYLES в нужном языке
        self.fields['favorite_styles'].choices = [
            (s['code'], s['labels'].get(lang, s['labels'].get('en'))) for s in STYLES
        ]
        # sizes (обычно не переводим)
        self.fields['preferred_sizes'].choices = [(s, s) for s in SIZES]