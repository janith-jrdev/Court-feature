from django.urls import path
from .views import *

urlpatterns = [
    path('registration/<int:category_id>', off_registration, name="offline_entry"),
    path('close_reg/<int:category_id>', close_categoryReg, name="close_reg"),
    path('create_fixture/<int:category_id>', fixturetype_form, name="create_fixture"),
    path('schedule_match/<int:category_id>', schedule_match, name="schedule_match"),
    path('scoring/<int:match_id>', increment_set_score, name="score_match"),
    path('complete_set/<int:match_id>', complete_set, name="complete_set"),
]

app_name = "api"