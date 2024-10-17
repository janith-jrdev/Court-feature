from functools import wraps
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *
from sportshunt.utils import construct_next_url
import inspect

def organizer_required(f):
    
    @wraps(f)
    def decorated_function(req,*args, **kwargs):
        if not req.user.is_authenticated:
            messages.error(req, "You need to login first")
            return redirect('core:login')
        
        if not req.user.additional_data:
            messages.error(req, "Please fill in your additional userdata")
            return redirect(construct_next_url(reverse('core:additional_userdata'), req.get_full_path()))
        
        elif not req.user.additional_data.is_organizer:
            messages.error(req, "You are not organizer")
            return redirect('core:index')
        
        return f(req,*args, **kwargs)
    return decorated_function
class ArgsValidator:
    def __init__(self, func):
        self.func = func
        wraps(func)(self)

    def __call__(self, req, *args, **kwargs):
        self.org_instance = self.get_organization(req)
        if not self.org_instance:
            messages.error(req, "Organization not found in session")
            return redirect('org:index')

        # Validate tournament and category
        for method_name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if method_name.startswith('validate_') and not method(req, kwargs):
                return redirect('org:index')

        return self.func(req, *args, **kwargs)

    def get_organization(self, req):
        org_session = req.session.get('organization')
        return Organization.objects.filter(id=org_session).first()

    def validate_tournament(self, req, kwargs):
        tournament_id = kwargs.get('tournament_id')
        if tournament_id:
            print("validating tournament")
            tournament = Tournament.objects.filter(id=tournament_id).first()
            if not tournament:
                messages.error(req, "Invalid Tournament")
                return False
            if tournament.organization != self.org_instance:
                messages.error(req, "You are not authorized for this Tournament")
                return False
        return True

    def validate_category(self, req, kwargs):
        category_id = kwargs.get('category_id')
        tournament_id = kwargs.get('tournament_id')
        if category_id:
            print("validating category")
            category = Category.objects.filter(id=category_id).first()
            if not category:
                messages.error(req, "Invalid Category")
                return False
            
            if category.tournament.organization != self.org_instance:
                messages.error(req, "You are not authorized for this Category")
                return False
            
            if tournament_id:
                tournament = Tournament.objects.filter(id=tournament_id).first()
                if not tournament:
                    messages.error(req, "Invalid Tournament")
                    return False

                if category.tournament != tournament:
                    messages.error(req, "Category does not belong to the Tournament")
                    return False
            return True
        return True
    
    def validate_match(self, req, kwargs):
        match_id = kwargs.get('match_id')
        if match_id:
            print("validating match")
            match = Match.objects.filter(id=match_id).first()
            if not match:
                messages.error(req, "Invalid Match")
                return False
            if match.category.tournament.organization != self.org_instance:
                messages.error(req, "You are not authorized for this Match")
                return False
        return True

def org_admin_required(f):
    @organizer_required
    @wraps(f)
    def _wrapped_view(req,*args, **kwargs):
        org_session = req.session.get('organization')
        if not req.session.get('organization'):
            messages.error(req, "Organization is required")
            return redirect('org:orgs')
        org_instance = Organization.objects.get(id=org_session)
        if org_instance.admin != req.user:
            messages.error(req, "You are not authorized for this Organization")
            return redirect('org:orgs')
        return f(req,*args, **kwargs)
    return _wrapped_view

def host_required(f):
    @wraps(f)
    @org_admin_required
    @ArgsValidator
    def _wrapped_view(req,*args, **kwargs):
        return f(req,*args, **kwargs)
    return _wrapped_view