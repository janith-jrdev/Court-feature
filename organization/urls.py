from django.urls import path
from .views import *
urlpatterns = [
    path("", index, name="index"),
    path("new/", organization_form, name="org_form"),
    path("orgs/", select_orgs, name="orgs"),
    path("new_tournament/", tournament_form, name="tournament_form"),
    path("tournaments/<int:tournament_id>/new_category/", category_form, name="category_form"),
    
]

app_name = "org"