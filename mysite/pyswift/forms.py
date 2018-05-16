from django import forms

class FileForm(forms.Form):
    onefile = forms.FileField()

    # def clean(self):
    #     upload_to = '/home/upfile'
    #     if not 'file' in self.cleaned_data:
    #         return self.cleaned_data
    #     upload_to += self.cleaned_data['file'].name