from django.urls import path
from .views import *

urlpatterns = [
    path("", index, name="index"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("userdata/", additionalUserdata_view, name="additional_userdata"), # change to api in future
    path("profile/", profile_view, name="profile"),
    path("tournaments/<int:tournament_id>/", tournament_view, name="tournament"),
    
    path("getting_started/", getting_started_view, name="getting_started"),
    # path("tournaments/<int:tournament_id>/<int:category_id>/", category_view, name="category"),
    path("checkout/", checkout, name="checkout"),
    # path("orders/", orders_view, name="orders"),
    path("T&C/", terms_conditions_view, name="terms_and_conditions"),
]

app_name = "core"