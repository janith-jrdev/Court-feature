from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from .models import *

def organizer_required(f):
    @wraps(f)
    def decorated_function(req,*args, **kwargs):
        if not req.user.additional_data.is_organizer:
            messages.error(req, "You are not organizer")
            return redirect('core:index')
        return f(req,*args, **kwargs)
    return decorated_function

def host_required(f):
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

        
        