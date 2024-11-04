from functools import wraps
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from sportshunt.utils import construct_next_url

def userdataDecorator(func):
    @wraps(func)
    def wrapper(req,*args, **kwargs):
        if not req.user.is_authenticated:
            return redirect(reverse('core:login'))
        if not req.user.has_additional_data:
            # messages.error(req, "User data already exists")
            return redirect(construct_next_url(reverse('core:additional_userdata'), req.get_full_path()))

        return func(req, *args, **kwargs)
    return wrapper