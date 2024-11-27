from django.urls import path
from .views import *

# need to rewrite the urls
urlpatterns = [
    path("", index, name="index"),
    path("new/", organization_form, name="org_form"),
    path("orgs/", select_orgs, name="orgs"),
    path("new_tournament/", tournament_form, name="tournament_form"),
    path("tournaments/<int:tournament_id>/new_category/", category_form, name="category_form"),
    path("tournaments/<int:tournament_id>/", tournament_view, name="tournament_view"),
    path("tournaments/<int:tournament_id>/<int:category_id>/", category_view, name="category_view"),
    path("tournaments/<int:tournament_id>/<int:category_id>/create_match/", manual_create_matches, name="create_match"),
    path("scheduled_matches/<int:category_id>/", scheduled_match_view, name="scheduled_matches"),
    path("scoring/<int:match_id>/", match_scoring, name="scoring"),
]

# path('tournament/create/', views.tournament_form, name='tournament_form'),
#     path('schedule_match/<int:category_id>/', views.schedule_match, name='schedule_match'),
#     path('score_match/<int:match_id>/', views.score_match, name='score_match'),

app_name = "org"