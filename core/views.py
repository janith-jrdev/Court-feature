from django.shortcuts import render, HttpResponse

# Create your views here.
def index(req):
    
    return HttpResponse("Hello Mesak!")