from django.urls import path
from .views import *

urlpatterns = [
    path("", index, name="index"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("userdata/", additionalUserdata_view, name="additional_userdata"),
    path("profile/", profile_view, name="profile"),
    path("tournaments/<int:tournament_id>/", tournament_view, name="tournament"),
    path("tournaments/<int:tournament_id>/<int:category_id>/", category_view, name="category"),
    path("checkout/", checkout, name="checkout"),
    path("orders/", orders_view, name="orders"),
]

app_name = "core"