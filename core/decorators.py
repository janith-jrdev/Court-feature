from functools import wraps
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages

def userdataDecorator(func):
    @wraps(func)
    def wrapper(req,*args, **kwargs):
        if not req.user.is_authenticated:
            return HttpResponseRedirect(reverse('core:login'))
        if req.user.additional_data:
            messages.error(req, "User data already exists")
            return HttpResponseRedirect(reverse('core:profile'))
        return func(req, *args, **kwargs)
    return wrapper