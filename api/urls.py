from django.urls import path
from .views import *

urlpatterns = [
    path('registration/<int:category_id>', off_registration, name="offline_entry"),
    path('close_reg/<int:category_id>', close_categoryReg, name="close_reg"),
    path('create_fixture/<int:category_id>', fixturetype_form, name="create_fixture"),
    path('schedule_matches/<int:category_id>', manual_schedule_matches, name="schedule_matches"),
]

app_name = "api"