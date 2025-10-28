from django import forms
from .models import GradeRecord

class GradeForm(forms.Form):
    student = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    subject = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    grade = forms.IntegerField(min_value=1, max_value=5, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    save_to = forms.ChoiceField(
        choices=[('file', 'В XML-файл'), ('db', 'В базу данных')],
        widget=forms.RadioSelect,
        initial='db'
    )

class UploadFileForm(forms.Form):
    file = forms.FileField(label="XML-файл", widget=forms.FileInput(attrs={'class': 'form-control'}))