from django.conf.urls.defaults import patterns, include, url
from socialrank_app.views import * 

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', main_page),
    (r'^test$', index),  
    (r'^test2/(\w+)$', test2),
    (r'^seedpages/', seed_pages),
    (r'^crawl/', crawl_daily),
    (r'^(\d+)/$', individual_page),
    (r'^top_pages$', top_pages), 


    # Examples:
    # url(r'^$', 'socialrank_project.views.home', name='home'),
    # url(r'^socialrank_project/', include('socialrank_project.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
