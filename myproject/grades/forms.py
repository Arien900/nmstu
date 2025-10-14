from django import forms

class GradeForm(forms.Form):
    student = forms.CharField(max_length=100)
    subject = forms.CharField(max_length=100)
    grade = forms.IntegerField(min_value=1, max_value=5)

class UploadFileForm(forms.Form):
    file = forms.FileField()