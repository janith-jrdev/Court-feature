from django.http import JsonResponse
from django.shortcuts import render
from .decorators import *
from .validators import *
from .models import *
from .serializer import *
import json
import math
# Create your views here.

@host_required
def index(req):
    org_id = req.session.get('organization')
    org = Organization.objects.get(id=org_id)
    past_tournaments = org.tournaments.filter(end_date__lt=datetime.now()).order_by('-start_date')
    upcoming_tournaments = org.tournaments.filter(start_date__gte=datetime.now()).order_by('start_date')
    print(past_tournaments, upcoming_tournaments)
    context = {
        'past_tournaments': past_tournaments,
        'upcoming_tournaments': upcoming_tournaments,
    }
    return render(req, "organization/index.html", context)

@organizer_required
def organization_form(req):
    # needs a decorator to check if the user is an organizer
    if req.method == "POST":
        if OrganizationValidator(req.POST, req).validatation:
            messages.success(req, "Organization created successfully")
            return redirect("org:index")    
    return render(req, "organization/create_organization.html")

@host_required
def tournament_form(req):
    if req.method == "POST":
        tournament_validator = TournamentValidator(req.POST, req)
        
        if tournament_validator.validatation:
            messages.success(req, "Tournament created successfully")
            tournament_id = tournament_validator.tournament_id
            return redirect("org:category_form", tournament_id=tournament_id)
        
    return render(req, "organization/create_tournament.html")

@organizer_required
def select_orgs(req):
    org_instances = Organization.objects.filter(admin=req.user)
    orgs = [org.id for org in org_instances]
    if req.method == "POST":
        org_id = req.POST.get("org")
        print(org_id)
        if org_id and int(org_id) in orgs:
            req.session['organization'] = org_id
            return redirect("org:index")
        messages.error(req, "Invalid Organization")
    
    if len(orgs) == 0:
        return redirect("org:org_form")
    
    if len(orgs) == 1:
        req.session['organization'] = orgs[0]
        return redirect("org:index")
    
    return render(req, "organization/select_organization.html", {"orgs": org_instances})

@host_required
def category_form(req, tournament_id):
    if req.method == "POST":
        category_validator = CategoryValidator(req.POST, req, tournament_id)
        if category_validator.validatation:
            messages.success(req, "Category created successfully")
            category_id = category_validator.category_id
            return redirect("org:category_view", tournament_id=tournament_id, category_id=category_id)
        
    return render(req, "organization/create_category.html", {"tournament_id": tournament_id})

@host_required
def tournament_view(req, tournament_id):
    tournament_instance = Tournament.objects.get(id=tournament_id)
    if tournament_instance.organization.admin != req.user:
        messages.error(req, "You are not authorized for this Tournament")
        return redirect("org:index")
    data = tournamentSerializer(tournament_instance)
    return render(req, "organization/tournament_view.html", {"tournament_data": data, "tournament": tournament_instance})

@host_required
def category_view(req, tournament_id, category_id):
    tournament = Tournament.objects.get(id=tournament_id)
    category = Category.objects.get(id=category_id)
    if tournament.organization.admin != req.user:
        messages.error(req, "You are not authorized for this Category")
        return redirect("org:index")
    data = {"category_data":categorySerializer(category), "category": category}
    
    if category.fixture and category.fixture.fixtureType == "KO":
        ko_instance = category.fixture.content_object
        fixture_json = json.dumps(ko_instance.json)
        data["fixture_json"] = fixture_json
        scheduled_matches = category.fixture.scheduled_matches.filter(match_state=False)
        data["scheduled_matches"] = scheduled_matches
    return render(req, "organization/category_view.html", data)

@host_required
def manual_create_matches(req, tournament_id, category_id):
    
    tournament = Tournament.objects.get(id=tournament_id)
    category = Category.objects.get(id=category_id)

    if category.fixture.fixtureType != "KO":
        messages.error(req, "Invalid Fixture Type this doesnt have manual scheduling")
        return redirect("org:index")
    
    ko_instance = category.fixture.content_object
    if not ko_instance.fixing_manual:
        messages.error(req, "Its automatic scheduling")
        return redirect("org:index")
    
    if req.method == "POST":
        _, info = ScheduleMatchValidator(req.body, category, ko_instance)
        if _:
            messages.success(req, info)
            return JsonResponse({"success": True, "info": info})
        messages.error(req, info)
        return JsonResponse({"success": False, "info": info})
    teams = category.teams.all()
    if category.fixture.fixtureType == "KO":
        teams = category.fixture.content_object.bracket_teams.all()


    category_teams = [{"id": team.id, "name":team.name } for team in teams]
    next_power_of_2 = 2 ** math.ceil(math.log2(len(teams)))
    byes = next_power_of_2 - len(teams)
    
    for i in range(byes):
        category_teams.append({"id": None, "name": "Bye"})
    
    category_teams= json.dumps(category_teams)

    return render(req, "organization/create_manual_matches.html", {"teams": category_teams, "category": category})

@host_required
def scheduled_match_view(req, category_id):
    category_instance = Category.objects.get(id=category_id)
    
    if not category_instance.fixture:
        messages.error(req, "No fixture for this category")
        return redirect("org:index") # redirect to category page, 
    
    scheduled_matches = category_instance.fixture.scheduled_matches.filter(match_state=False)
    if not scheduled_matches:
        messages.error(req, "No scheduled matches")
        return redirect("org:index") # redirect to category page,
    return render(req, "organization/scheduled_matches.html", {"matches": scheduled_matches})

@host_required
def match_scoring(req, match_id):
    match_instance = Match.objects.get(id=match_id)
    
    if match_instance.match_state:
        messages.error(req, "Match is already completed")
        return redirect("org:index")
    
    if match_instance.id not in match_instance.category.fixture.scheduled_matches.values_list('id', flat=True):
        messages.error(req, "Match not scheduled")
        return redirect("org:index")  # Redirect to category page

    scores = [{'team1': set_data.team1_score, 'team2': set_data.team2_score} for set_data in match_instance.sets.all()]
    team_wins = {
        'team1': sum(1 for set_data in match_instance.sets.all() if set_data.set_state and set_data.winner == match_instance.team1),
        'team2': sum(1 for set_data in match_instance.sets.all() if set_data.set_state and set_data.winner == match_instance.team2)
    }

    return render(req, "organization/match_scoring.html", {"match_data": match_instance, "scores": scores, "team_wins": team_wins})
