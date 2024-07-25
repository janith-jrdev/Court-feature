from django.shortcuts import render
from .decorators import *
# Create your views here.

@organizer_required
def index(req):
    return render(req, "organization/index.html")