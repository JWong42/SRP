from django.db import models

# Create your models here.

class Page(models.Model): 
    name = models.CharField(max_length=100)
    link = models.URLField()
#    pic = models.ImageField()

class Friends(models.Model):
    page = models.ForeignKey(Page)
    following = models.IntegerField()
    followers = models.IntegerField()
    date = models.DateField()
    
class Upload_SeedPages(models.Model):
    seedpage_file = models.FileField(upload_to='/uploads/seedpages/')
    seedpage_link = models.URLField()
    

