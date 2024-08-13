from django.urls import path
from .views import *
urlpatterns = [
    path("", index, name="index"),
    path("new/", organization_form, name="org_form"),
    path("orgs/", select_orgs, name="orgs"),
    path("new_tournament/", tournament_form, name="tournament_form"),
    path("tournaments/<int:tournament_id>/new_category/", category_form, name="category_form"),
    path("tournaments/<int:tournament_id>/", tournament_view, name="tournament_view"),
    path("tournaments/<int:tournament_id>/<int:category_id>/", category_view, name="categories"),
    path("tournaments/<int:tournament_id>/<int:category_id>/schedule_match/", manual_schedule_matches, name="schedule_match"),
    
]

app_name = "org"