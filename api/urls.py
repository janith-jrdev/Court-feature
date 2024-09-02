from django.urls import path
from .views import *

urlpatterns = [
    path('registration/<int:category_id>', off_registration, name="offline_entry"),
    path('close_reg/<int:category_id>', close_categoryReg, name="close_reg"),
    path('create_fixture/<int:category_id>', fixturetype_form, name="create_fixture"),
    path('schedule_match/<int:category_id>', schedule_match, name="schedule_match"),
    path('create_order', create_order, name="create_order"),
]

app_name = "api"