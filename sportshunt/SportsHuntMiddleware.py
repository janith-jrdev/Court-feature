from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.utils.http import url_has_allowed_host_and_scheme

class NextParameterMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if isinstance(response, HttpResponseRedirect):
            next_url = request.GET.get('next')
            if next_url and self.is_safe_url(next_url, request):
                return redirect(next_url)
        return response

    def is_safe_url(self, url, request):
        return url_has_allowed_host_and_scheme(url, allowed_hosts=[request.get_host()])