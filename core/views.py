from django.shortcuts import render, HttpResponse, redirect
from .models import *
from django.contrib.auth import logout 
from django.urls import reverse
from decouple import config
from .validator import addtionalUserData_validator
from .decorators import *
from sportshunt.utils import *
from django.utils import timezone, dateformat
from datetime import timedelta, datetime
from organization.models import *

# Create your views here.
def index(req):
    now_date = datetime.now().date()
    end_date = now_date + timedelta(days=15)
    
    upcoming_tournaments = Tournament.objects.filter(start_date__gte=now_date, start_date__lte=end_date).order_by('start_date')[:8]
    ongoing_tournaments = Tournament.objects.filter(start_date__lte=now_date, end_date__gte=now_date).order_by('start_date')[:8]
    
    return render(req, 'core/index.html', {
        "upcoming_tournaments": upcoming_tournaments,
        "ongoing_tournaments": ongoing_tournaments,
    })

def login_view(req):
    return HttpResponseRedirect(reverse('social:begin', args=['auth0']))

def logout_view(req):
    req.session.flush()
    logout(req)
    
    domain = config('AUTH0_DOMAIN')
    client_id = config('AUTH0_CLIENT_ID')
    return_to = req.build_absolute_uri(reverse('core:index'))
    
    return HttpResponseRedirect(f"https://{domain}/v2/logout?client_id={client_id}&returnTo={return_to}")

@userdataDecorator
def additionalUserdata_view(req):
    if req.method == 'POST':
        if addtionalUserData_validator(req.POST, req):
            messages.success(req, "Additional User Data added successfully")
            return HttpResponseRedirect(reverse('core:index'))
        
        messages.error(req, "Error Occured")
    return render(req, 'core/additional_userdata.html') 

def profile_view(req):
    # future add like a serializer to get the user data [ if custom profile then send that or else the other one]
    if not req.user.is_authenticated:
        return redirect(reverse('core:login'))
    
    if not req.user.additional_data:
        messages.info(req, "Please fill in your additional userdata")
        url = construct_next_url(reverse('core:additional_userdata'), req.path)
        return redirect(url)
    
    auth0_user = None
    if req.user.social_auth.exists():
        auth0_user = req.user.social_auth.get(provider="auth0")
    return render(req, 'core/profile.html', {
        "auth0_user": auth0_user,
    })

# do validation in decorator    

def tournament_view(req, tournament_id):
    tournament_instance = Tournament.objects.get(id=tournament_id)
    return render(req, 'core/tournament_view.html', {
        "tournament": tournament_instance,
    })
    
def category_view(req, tournament_id, category_id):
    tournament_instance = Tournament.objects.get(id=tournament_id)
    category_instance = Category.objects.get(id=category_id)
    return render(req, 'core/category_view.html', {
        "tournament": tournament_instance,
        "category": category_instance,
    })