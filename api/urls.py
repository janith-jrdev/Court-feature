from django.urls import path
from .views import *

urlpatterns = [
    path('registration/<int:category_id>', off_registration, name="offline_entry"),
    path('close_reg/<int:category_id>', close_categoryReg, name="close_reg"),
    path('create_fixture/<int:category_id>', fixturetype_form, name="create_fixture"),
]

app_name = "api"