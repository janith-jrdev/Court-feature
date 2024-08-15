from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from organization.models import *
import json
from django.core.exceptions import ObjectDoesNotExist
from organization.validators import *
import math

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


def close_categoryReg(req, category_id):
    # need to add more validation
    category_instance = Category.objects.get(id=category_id)
    org_instance = category_instance.tournament.organization

    if req.user != org_instance.admin:
        return JsonResponse({"message": "User not authorized"}, status=403)
    
    category_instance.registration_status = False
    category_instance.save()
    
    return JsonResponse({"message": "Registration closed successfully"})

def fixturetype_form(req, category_id):
    category_instance = Category.objects.get(id=category_id)
    org_instance = category_instance.tournament.organization

    if req.user != org_instance.admin:
        return JsonResponse({"message": "User not authorized"}, status=403)
    
    if req.method == "POST":
        data = json.loads(req.body)
        print(data)
        
        fixture_type = data.get('fixture_type')
        
        if not fixture_type:
            return JsonResponse({"message": "Fixture type cannot be empty"}, status=400)
        
        if fixture_type not in ['KO']: #, 'RR', 'RR_KO' add these later
            return JsonResponse({"message": "Invalid fixture type"}, status=400)
        
        fixture_instance = Fixture.objects.create(fixtureType=fixture_type, category=category_instance)
        
        if fixture_type == 'KO':
            fixture_mode = data.get('fixture_mode')
            ko_instance = Knockout.objects.create(category=category_instance, fixing_manual=True)
            ko_instance.bracket_teams.set(category_instance.teams.all())
            
            no_teams = category_instance.teams.count()
            nearest_power_of_2 = 2 ** math.ceil(math.log2(no_teams))
            byesNeeded = nearest_power_of_2 - no_teams
            cur_lvl =  math.ceil(math.log2(no_teams)) -1
            ko_instance.ko_stage = cur_lvl
            
            fixture_instance.content_object = ko_instance
            fixture_instance.save()
            category_instance.fixture = fixture_instance
            category_instance.save()
            

            return JsonResponse({"message": "Fixture type updated successfully"})
        
        return JsonResponse({"message": "some server side error"}, status=500)
    
    return JsonResponse({"message": "Invalid request method"}, status=400)

def schedule_match(req, category_id):
    category_instance = Category.objects.get(id=category_id)
    org_instance = category_instance.tournament.organization

    if req.user != org_instance.admin:
        return JsonResponse({"message": "User not authorized"}, status=403)
    
    if req.method != "POST":
        return JsonResponse({"message": "Invalid request method"}, status=400)
    
    data = json.loads(req.body)
    
    fixture_instance = category_instance.fixture
    
    if not fixture_instance:
        return JsonResponse({"message": "Fixture not created yet"}, status=400)
    
    print(data)
    if fixture_instance.fixtureType == 'KO':
        ko_instance = fixture_instance.content_object
        bracket_matches =[match.id for match in  ko_instance.bracket_matches.all()]
        
        match_id = int(data.get('match'))
        if not match_id in bracket_matches:
            return JsonResponse({"message": "Match not in bracket matches"}, status=400)
        
        noSets = int(data.get('no_sets'))
        match_instance = Match.objects.get(id=match_id)
        match_instance.no_sets = noSets
        match_instance.save()
        
        # create sets and assign em
        for i in range(noSets):
            set_instance = SetScoreboard.objects.create(set_no=i+1, match=match_instance)
            set_instance.win_points = int(data.get("set_winning_points"))
            match_instance.sets.add(set_instance)
        
        match_instance.current_set = SetScoreboard.objects.get(set_no=1, match=match_instance)
        match_instance.save()
        
        fixture_instance.scheduled_matches.add(match_instance)
        fixture_instance.save()
        ko_instance.bracket_matches.remove(match_instance)
        ko_instance.save()
        return JsonResponse({"message": "Match scheduled successfully"})
    
    return JsonResponse({"message": "Other fixture types are not created yet"}, status=500)
        