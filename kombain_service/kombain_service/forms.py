from django import forms
from django.core.exceptions import ValidationError


class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=128)
    file = forms.FileField()

    def clean_file(self):
        file = self.cleaned_data['file']
        formats_file = ['pdf', 'html']
        split_file = file.name.lower().split('.')
        format_file = split_file[len(split_file)-1]
        if format_file not in formats_file:
            raise ValidationError(f'Поддерживаются только {formats_file} форматы')