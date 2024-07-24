from django.shortcuts import render, HttpResponse, redirect
from .models import *
from django.contrib.auth import logout 
from django.urls import reverse
from decouple import config
from .validator import addtionalUserData_validator
from .decorators import *
from urllib.parse import urlencode

# Create your views here.
def index(req):
    if req.user.is_authenticated:
        return HttpResponse(f"Hello {req.user} ! You are logged in.")
    return HttpResponse("Hello World ! You are not logged in.")

def login_view(req):
    return HttpResponseRedirect(reverse('social:begin', args=['auth0']))

def logout_view(req):
    logout(req)
    
    domain = config('AUTH0_DOMAIN')
    client_id = config('AUTH0_CLIENT_ID')
    return_to = req.build_absolute_uri(reverse('index'))
    
    return HttpResponseRedirect(f"https://{domain}/v2/logout?client_id={client_id}&returnTo={return_to}")

@userdataDecorator
def additionalUserdata_view(req):
    if req.method == 'POST':
        if addtionalUserData_validator(req.POST, req.user):
            messages.success(req, "Additional User Data added successfully")
            return HttpResponseRedirect(reverse('index'))
        
        messages.error(req, "Error Occured")
    return render(req, 'core/additional_userdata.html') 

def profile_view(req):
    # future add like a serializer to get the user data [ if custom profile then send that or else the other one]
    if not req.user.is_authenticated:
        return redirect(reverse('login'))
    
    if not req.user.additional_data:
        messages.info(req, "Please fill in your additional userdata")
        base_url = reverse('additional_userdata')
        query_string = urlencode({'next': req.path})
        url = f'{base_url}?{query_string}'
        print(url)
        return redirect(url)
    
    auth0_user = req.user.social_auth.get(provider="auth0")
    

    return render(req, 'core/profile.html', {
        "auth0_user": auth0_user,
    })