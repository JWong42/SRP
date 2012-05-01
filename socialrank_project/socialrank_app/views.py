from django.http import HttpResponse
from django.shortcuts import render_to_response 
from django.shortcuts import redirect 
from django.template import RequestContext 
from django.db.models import Q
from socialrank_app.models import * 
from socialrank_app.forms import AddPageForm
from socialrank_app.forms import SeedPagesForm 
from urllib2 import urlopen 
from BeautifulSoup import BeautifulSoup
import datetime
import time 
import calendar
import re 
import json 


def main_page(request):    
    # Select the friends statistics of pages for today and order from highest followers to lowest 
     
    pages = Friends.objects.filter(date=datetime.date.today()).order_by('-followers')
    
    if not pages: 
        recent_date = Friends.objects.order_by('-date')[0].date
        pages = Friends.objects.filter(date=recent_date).order_by('-followers')
         
    rank = 1 
    brands = []
    
    for page_object in pages: 
        
        brand = {}       
            
        brand['rank'] = rank 
        rank += 1 
        name = page_object.page.name 
        name = re.sub('amp;', '', name)
        brand['name'] = name
        link = str(page_object.page.link)
        link = re.search('[0-9]+', link).group(0)
        link = int(link)
        brand['link'] = link 
        brand['img'] = page_object.page.img_link
        brand['following'] = page_object.following
        brand['followers'] = page_object.followers
        brands.append(brand) 
            
    errors = []   
    if 'p' in request.POST:
        page_id = request.POST['p']
        if not page_id: 
            errors.append('Please enter a G+ Profile ID to add!')
        elif not isinstance(page_id, int) and len(page_id) != 21: 
            errors.append('Please enter only the G+ Profile ID!') 
        else:        
            url = 'https://plus.google.com/' + page_id 
               
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
            page_name = re.sub('amp;', '', page_name)
                   
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
                  
            friends,created_dummy = Friends.objects.get_or_create(
                       page = page, 
                       date = datetime.date.today())  
                
            friends.following = no_following
            friends.followers = no_followers 
                    
            friends.save()
                
            return redirect('/' + page_id)    
                    
    #    else: 
    #        form = AddPageForm()
    
    variables = RequestContext(request, {
        'head_title' : u'Django SocialRank', 
        'page_title' : u'Welcome to Social Rank', 
        'page_body' : u"Where you can check and evaluate your brand's social status!!",    
        'brands' : brands,
        'errors' : errors, 
    #        'form' : form, 
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
                
                friends,created_dummy = Friends.objects.get_or_create(
                       page = page, 
                       date = datetime.date.today())  
            
                friends.following = no_following
                friends.followers = no_followers 
                
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
        page_name = re.sub('amp;', '', page_name)
               
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
            
        friends,created_dummy = Friends.objects.get_or_create(
                       page = page, 
                       date = datetime.date.today(),
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
    name = re.sub('amp;', '', name)
    friends_set = page.friends_set.all()
    
    results = []
    results2 = []

    for i in range(len(friends_set)): 
        date = friends_set[i].date
        date = calendar.timegm(date.timetuple())        
        date = date * 1000 
        date2 = friends_set[i].date.strftime("%m-%d-%Y")
#         date = time.mktime(date.timetuple())
        following = friends_set[i].following 
        followers = friends_set[i].followers

        if friends_set[0].id == friends_set[i].id: 
            growth = 0
        else:         
            growth = friends_set[i].followers - friends_set[i-1].followers 

        results.append([date, followers])
        results2.append([date2, following, followers, growth])
    
    results2.reverse()
         
    variables = RequestContext(request, {
        'name' : name,
        'results' : results,  
        'results2' : results2,
    })
    
    return render_to_response('individual_page.html', variables)

def index(request): 
    flag = False 
    word = ''
    errors = []
#    if request.method == "POST":
#    if request.POST['p']: 
    if 'p' in request.POST:
#        flag = True 
#        word = 'hello'
        p = request.POST['p']
        if not p: 
            errors.append('Enter a search term.')
        elif len(p) > 6: 
            errors.append('Please enter more than 6 characters.')
        else: 
            flag = True 
            word = 'hello' 


    return render_to_response('index.html', RequestContext(request, {'flag' : flag, 'word' : word, 'errors' : errors} ))

def test2(request, query): 
    query = query
    query = query.strip()
    if query:    
        keywords = query.split()
        q = Q()
        for keyword in keywords: 
            q = q & Q(name__icontains=keyword)
        pages = Pages.objects.filter(q)[:5]
        result = []
        for page in pages: 
            link = page.link
            id = str(re.findall('(\d+)', link))
            name = str(page.name)
            data = {}
            data['id'] = id
            data['page'] = name
            result.append(data)
        result = json.dumps(result)
        return HttpResponse(result)
             
#        obj = [{'id': '1234','name': 'Joe', }, {'id': '5678','name': 'Henry'}]
#        data = json.dumps(obj)
#        return HttpResponse(data)

 #   if 'data' in request.GET: 
 #       query = request.GET['data'].strip()
 #       if query: 
 #           keywords = query.split()
 #           q = Q() 
 #           for keyword in keywords: 
 #               q = q & Q(name__icontains=keyword)
 #           pages = Pages.objects.filter(q)
 #           result = []
 #           for page in pages: 
 #               link = page.link 
 #               id = str(re.findall('(\d+)', link))
 #               name = str(page.name)
 #               data = {}
 #               data['ID'] = id 
 #               data['Page'] = name
 #               result.append(data)
 #           result = json.dumps(result)
 #           return HttpResponse(result)
 #       else: 
 #           result = ''
 #           return HttpResponse(result)  
    
    
    
    
    
