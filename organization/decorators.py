from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def organizer_required(f):
    @wraps(f)
    def decorated_function(req,*args, **kwargs):
        if not req.user.additional_data.is_organizer:
            messages.error(req, "You are not organizer")
            return redirect('core:index')
        return f(req,*args, **kwargs)
    return decorated_function