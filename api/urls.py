from django.urls import path
from .views import *

urlpatterns = [
    path('registration/<int:category_id>', off_registration, name="offline_entry"),
    path('close_reg/<int:category_id>', close_categoryReg, name="close_reg"),
    path('create_fixture/<int:category_id>', fixturetype_form, name="create_fixture"),
    path('schedule_match/<int:category_id>', schedule_match, name="schedule_match"),
    path('scoring/<int:match_id>', score_match, name="score_match"),
    path('create_order', create_order, name="create_order"),
    path('create_match_ko/<int:category_id>', create_matches_ko_manual, name="create_match_ko"),
    
    path('create_order/', create_order, name="create_order"),
]

app_name = "api"