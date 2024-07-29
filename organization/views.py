from django.shortcuts import render
from .decorators import *
from .validators import *
from .models import *
# Create your views here.

@host_required
def index(req):
    return render(req, "organization/index.html")

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
        if TournamentValidator(req.POST, req).validatation:
            messages.success(req, "Tournament created successfully")
            return redirect("org:index")
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


def category_form(req, tournament_id):
    print(tournament_id)
    if req.method == "POST":
        print(tournament_id)
        if CategoryValidator(req.POST, req, tournament_id).validatation:
            messages.success(req, "Category created successfully")
            return redirect("org:index")
    return render(req, "organization/create_category.html", {"tournament_id": tournament_id})

 