from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from organization.models import Category, Team
import json

def off_registration(req, category_id):
    if req.method != "POST":
        return JsonResponse({"message": "Invalid request method"}, status=400)
    
    if not req.user.is_authenticated:
        return JsonResponse({"message": "User not authenticated"}, status=403)
    
    if not req.user.additional_data.is_organizer:
        return JsonResponse({"message": "User not authorized"}, status=403)
    
    category_instance = get_object_or_404(Category, id=category_id)
    org_instance = category_instance.tournament.organization
    
    if org_instance.admin != req.user:
        return JsonResponse({"message": "User not authorized"}, status=403)
    
    try:
        data = json.loads(req.body)
        team_name = data.get('team_name')
        
        if not team_name:
            return JsonResponse({"message": "Team name cannot be empty"}, status=400)
        
        Team.objects.create(
            name=team_name,
            category=category_instance
        )
        
        return JsonResponse({"message": "Registration successfully"})
    except json.JSONDecodeError:
        return JsonResponse({"message": "Invalid JSON data"}, status=400)
