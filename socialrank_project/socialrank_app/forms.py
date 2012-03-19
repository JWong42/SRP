from django import forms 

#from socialrank_app.models import * 
#from django.forms import ModelForm

#class SeedpagesForm(ModelForm): 
#    class Meta: 
#        model = Upload_SeedPages
#        fields = ('seedpage_file',)
 
class AddPageForm(forms.Form): 
    id = forms.CharField()

class SeedPagesForm(forms.Form): 
    file = forms.FileField()
