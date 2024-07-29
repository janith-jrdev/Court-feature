from django.urls import path
from .views import *

urlpatterns = [
    path('registration/<int:category_id>', off_registration, name="offline_entry"),
]

app_name = "api"