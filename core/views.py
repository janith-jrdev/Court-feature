from django.shortcuts import render, HttpResponse, redirect, HttpResponseRedirect
from .models import *
from django.contrib.auth import logout 
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from .validator import addtionalUserData_validator
from .decorators import *
from sportshunt.utils import *
from django.utils import timezone, dateformat
from datetime import timedelta, datetime
from organization.models import *
import razorpay
from django.conf import settings
import os

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
    
    domain = os.getenv('AUTH0_DOMAIN')
    client_id = os.getenv('AUTH0_CLIENT_ID')
    return_to = req.build_absolute_uri(reverse('core:index'))
    
    return HttpResponseRedirect(f"https://{domain}/v2/logout?client_id={client_id}&returnTo={return_to}")

def additionalUserdata_view(req):
    if req.method == 'POST':
        if addtionalUserData_validator(req.POST, req):
            messages.success(req, "Additional User Data added successfully")
            return HttpResponseRedirect(reverse('core:index'))
        
        messages.error(req, "Error Occured")
    return render(req, 'core/additional_userdata.html') 

@userdataDecorator
def profile_view(req):
    # future add like a serializer to get the user data [ if custom profile then send that or else the other one]
    
    auth0_user = None
    if req.user.social_auth.exists():
        auth0_user = req.user.social_auth.get(provider="auth0")
    return render(req, 'core/profile.html', {
        "auth0_user": auth0_user,
    })

    

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
    
@csrf_exempt
def checkout(req):
    if req.method != "POST":
        return render(req, "errors/404.html")
    
    payment_id = req.POST.get('razorpay_payment_id', '')
    razorpay_order_id = req.POST.get('razorpay_order_id', '')
    signature = req.POST.get('razorpay_signature', '')
    
    params_dict = {
        'razorpay_order_id': razorpay_order_id,
        'razorpay_payment_id': payment_id,
        'razorpay_signature': signature
    }

    if Order.objects.filter(order_id=razorpay_order_id).exists():
        order_instance = Order.objects.get(order_id=razorpay_order_id)
        razorpay_client = razorpay.Client(auth=(settings.RAZOR_KEY_ID,
                                settings.RAZOR_KEY_SECRET)) 
        
        result = razorpay_client.utility.verify_payment_signature(params_dict)
        if result is not None:
            amount = order_instance.amount
            try:
                razorpay_client.payment.capture(payment_id, amount)
                order_instance.status = True
                order_instance.signature = signature
                order_instance.payment_id = payment_id
                order_instance.save()
                order_details = order_instance.order_details
                team_name = order_details.team_name
                category_instance = order_details.category
                
                Team.objects.create(name=team_name, category=category_instance)
                
                messages.add_message(req, messages.SUCCESS, f'Payment successful, and {team_name} is reqisted')
                return redirect('core:category', category_instance.tournament.id, category_instance.id)
                
                
            except Exception as e:
                messages.add_message(req, messages.ERROR, f'Payment failed {e}')
                return redirect('core:index') # take to a error page and a btn to go back using js windows prev or something
            
        return render(req, "payments/failed.html") # make a file like that

    return render(req, "payments/failed.html")


@userdataDecorator
def orders_view(req):
    orders = Order.objects.filter(user=req.user)
    return render(req, 'core/orders.html', {
        "orders": orders,
    })
    
def getting_started_view(req):
    # return render(req, 'core/getting_started.html')
    return HttpResponse("<h1>Getting Started</h1>")