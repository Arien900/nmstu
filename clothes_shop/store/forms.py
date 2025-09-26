from django import forms
from .data import STYLES, SIZES

STYLE_CHOICES = [(s['code'], s['label']) for s in STYLES]
SIZE_CHOICES = [(s, s) for s in SIZES]

class SettingsForm(forms.Form):
    theme = forms.ChoiceField(choices=[('light', 'Light'), ('dark', 'Dark')], required=False)
    language = forms.ChoiceField(choices=[('en', 'English'), ('ru', 'Русский')], required=False)
    favorite_styles = forms.MultipleChoiceField(choices=STYLE_CHOICES, required=False, widget=forms.CheckboxSelectMultiple)
    preferred_sizes = forms.MultipleChoiceField(choices=SIZE_CHOICES, required=False, widget=forms.CheckboxSelectMultiple)