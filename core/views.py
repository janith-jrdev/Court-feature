from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from .models import User
from django.contrib.auth import logout 
from django.urls import reverse
from decouple import config

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