from django.db import models

class Pages(models.Model): 
    name = models.CharField(max_length=100, null=False, blank=False)
    link = models.URLField(unique=True, null=False, blank=False)
    img_link = models.URLField(null=True)
    
    def __unicode__(self): 
        return self.name

class Friends(models.Model):
    page = models.ForeignKey(Pages)
    following = models.IntegerField()
    followers = models.IntegerField()
    date = models.DateField(auto_now_add=True)
    
    def __unicode__(self): 
        return u'%s, %s, %s' %(self.page.name, self.followers, self.date)
    

