from functools import wraps
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from organization.models import *
import json

def post_method_required(f):
    @wraps(f)
    def decorated_function(req, *args, **kwargs):
        if req.method != "POST":
            return JsonResponse({"message": "Invalid request method"}, status=400)
        return f(req, *args, **kwargs)
    return decorated_function

def login_required(f):
    @wraps(f)
    @post_method_required
    def decorated_function(req, *args, **kwargs):
        if not req.user.is_authenticated:
            return JsonResponse({"message": "User not authenticated"}, status=403)
        return f(req, *args, **kwargs)
    return decorated_function

def organizer_required(f):
    @wraps(f)
    @login_required
    def decorated_function(req, *args, **kwargs):
        if not req.user.additional_data.is_organizer:
            return JsonResponse({"message": "User not authorized"}, status=403)
        return f(req, *args, **kwargs)
    return decorated_function

def host_required(f):
    @wraps(f)
    @organizer_required
    def decorated_function(req, *args, **kwargs):
        if 'tournament_id' in kwargs:
            tournament = get_object_or_404(Tournament, id=kwargs['tournament_id'])
            if tournament.organization.admin != req.user:
                return JsonResponse({"message": "User not authorized"}, status=403)
            
        if 'category_id' in kwargs:
            category = get_object_or_404(Category, id=kwargs['category_id'])
            if category.tournament.organization.admin != req.user:
                return JsonResponse({"message": "User not authorized"}, status=403)
            
        if 'match_id' in kwargs:
            match = get_object_or_404(Match, id=kwargs['match_id'])
            if match.category.tournament.organization.admin != req.user:
                return JsonResponse({"message": "User not authorized"}, status=403)
            
        
        return f(req, *args, **kwargs)
    return decorated_function



def valid_json_data(f):
    @wraps(f)
    def decorated_function(req, *args, **kwargs):
        try:
            data = json.loads(req.body)
            req.data = data
        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON data"}, status=400)
        return f(req, *args, **kwargs)
    return decorated_function


