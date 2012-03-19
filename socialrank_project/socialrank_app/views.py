from django.http import HttpResponse
from django.shortcuts import render_to_response 
from django.shortcuts import redirect 
from django.template import RequestContext 
from socialrank_app.models import * 
from socialrank_app.forms import SeedPagesForm 
from socialrank_app.forms import TestForm
from urllib2 import urlopen 
from BeautifulSoup import BeautifulSoup
import datetime
import time 
import calendar
import re 


def main_page(request):

    # filter the Friends model of all pages with the latest date/time (or today)  - then sort from highest to lowest - then use [0:10] to slice the first 10 pages
    # use datetime.date.today() to select pages with follower numbers for today
    
    brands = []
    
    # Select the friends statistics of pages for today and order from highest followers to lowest 
    pages = Friends.objects.filter(date=datetime.date.today()).order_by('-followers')
    
    for page_object in pages: 
        
        brand = {}
        
        brand['name'] = page_object.page.name
        link = str(page_object.page.link)
        link = re.search('[0-9]+', link).group(0)
        link = int(link)
        brand['link'] = link 
        brand['img'] = page_object.page.img_link
        brand['following'] = page_object.following
        brand['followers'] = page_object.followers
        brands.append(brand) 
         
    variables = RequestContext(request, {
        'head_title' : u'Django SocialRank', 
        'page_title' : u'Welcome to SocialRank', 
        'page_body' : u"Where you can check and evaluate your brand's social status!!",    
        'brands' : brands,
    })     
    return render_to_response(
        'main_page.html', variables) 
    
def seed_pages(request): 
    if request.method == 'POST': 
        form = SeedPagesForm(request.POST, request.FILES)
        if form.is_valid():
            submitted_file = form.cleaned_data['file']
            submitted_file.seek(0)
            
            pages = []                        
            
            for url in submitted_file: 
                site = {}
                        
                result = urlopen(url)
                soup = BeautifulSoup(result)                 
                 
                #brand's page name                  
                page_name = soup.find('span', {"class" : "fn"})
                page_name = str(page_name) 
                page_name = re.search('\>(.*?)<', page_name) 
                try: 
                    page_name = page_name.group(0)
                except AttributeError: 
                    page_name = '><'
                page_name = re.sub('amp;','', page_name)
                page_name = page_name.strip('>' + '<') 
                site['name'] = page_name
                
                site['url'] = url 
                
                #brand's image                 
                img = soup.find('img', {"class" : "kM5Oeb-wsYqfb photo"})
                img = img["src"]
                img = img.strip('//')
                img = img.encode('utf-8')
                site['img'] = img
                
                #brand's no_following                 
                a = soup.find('h4', {"class" : "nPQ0Mb c-wa-Da" })
                a = str(a)
                a1 = re.search('\(\w+\)', a)
                try: 
                    a2 = a1.group(0)
                except AttributeError: 
                    a2 = '(0)'
                no_following = a2.strip('(' + ')')
                no_following= int(no_following)
                site['following'] = no_following
                
                
                #brand's no_followers                
                b = soup.find('h4', {"class" : "nPQ0Mb pD8zNd" }) 
                b = str(b)
                b1 = re.search('\(\w+\)', b)
                try: 
                    b2 = b1.group(0)
                except AttributeError: 
                    b2 = '(0)'
                no_followers = b2.strip('(' + ')')
                no_followers = int(no_followers)
                site['followers'] = no_followers 
                
                #since link column in model is unique, get the existing page by its url or create a new one
                page,created = Pages.objects.get_or_create( 
                               link = url                     
                               ) 
                #updage page's name and page's img link               
                page.name = page_name
                page.img_link = img 
                page.save() 
                
                friends = Friends(
                          page = page,
                          following = no_following,
                          followers = no_followers
                          )
                friends.save()
               
                pages.append(site)         
                                         
            variables = {
                 'pages' : pages
            }
            return render_to_response('seedpages_report.html', variables)
    else:    
        form = SeedPagesForm()
        
    context = {
        'form': form 
    }
    return render_to_response('seedpages_form.html', context, RequestContext(request))
    
def crawl_daily(request): 
    #grab all pages stored in the database
    pages = Pages.objects.all() 
    
    #number of pages crawled
    count = len(pages) 
    
    for page in pages: 
        url = page.link 
                
        result = urlopen(url)
        soup = BeautifulSoup(result)                 
                 
        #brand's page name                  
        page_name = soup.find('span', {"class" : "fn"})
        page_name = str(page_name) 
        page_name = re.search('\>(.*?)<', page_name) 
        try: 
            page_name = page_name.group(0)
        except AttributeError: 
            page_name = '><'
        page_name = page_name.strip('>' + '<') 
               
        #brand's image                
        img = soup.find('img', {"class" : "kM5Oeb-wsYqfb photo"})
        img = img["src"]
        img = img.strip('//')
        img = img.encode('utf-8')
                
        #brand's no_following                
        a = soup.find('h4', {"class" : "nPQ0Mb c-wa-Da" })
        a = str(a)
        a1 = re.search('\(\w+\)', a)
        try: 
            a2 = a1.group(0)
        except AttributeError: 
            a2 = '(0)'
        no_following = a2.strip('(' + ')')
        no_following= int(no_following)
                            
        #brand's no_followers               
        b = soup.find('h4', {"class" : "nPQ0Mb pD8zNd" }) 
        b = str(b)
        b1 = re.search('\(\w+\)', b)
        try: 
            b2 = b1.group(0)
        except AttributeError: 
            b2 = '(0)'
        no_followers = b2.strip('(' + ')')
        no_followers = int(no_followers)
                
        #since link column in model is unique, get the existing page by its url or create a new one
        page,created = Pages.objects.get_or_create( 
                       link = url                     
                     ) 
        #updage page's name and page's img link               
        page.name = page_name
        page.img_link = img 
        page.save() 
                
        friends = Friends(
                  page = page,
                  following = no_following,
                  followers = no_followers
                )
        friends.save()                       
                                         
    variables = {
                 'count' : count
                } 
    return render_to_response('crawl_report.html', variables)

def individual_page(request, page_id): 

    page = Pages.objects.get(link__contains=page_id)
    name = page.name 
    friends_set = page.friends_set.all()
    
    results = []
    results2 = []
    
    for each in friends_set:
        date = each.date
        date = calendar.timegm(date.timetuple())        
        date = date * 1000 
        date2 = each.date.strftime("%m-%d-%Y")
#         date = time.mktime(date.timetuple())
        following = each.following 
        followers = each.followers
        results.append([date, followers])
        results2.append([date2, following, followers])
    
    results2.reverse()
         
    variables = RequestContext(request, {
        'name' : name,
        'results' : results,  
        'results2' : results2,
    })
    
    return render_to_response('individual_page.html', variables)

