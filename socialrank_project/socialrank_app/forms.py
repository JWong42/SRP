from django import forms 

#class SeedpagesForm(forms.Form): 
#    file = forms.FileField()


#from socialrank_app.models import * 
#from django.forms import ModelForm

#class SeedpagesForm(ModelForm): 
#    class Meta: 
#        model = Upload_SeedPages
#        fields = ('seedpage_file',)

class TestForm(forms.Form): 
#    name = forms.CharField()
    file = forms.FileField()    
    
class SeedPagesForm(forms.Form): 
    file = forms.FileField()
