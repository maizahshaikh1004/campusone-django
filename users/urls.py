from django.urls import path
from . import views

urlpatterns=[
    path(
        "register/",
        views.register_request,
        name="register_request"
    ),
    path(
        "set-password/<int:user_id>/",
        views.set_password,
        name="set_password"
    ),
    path("login/",
    views.login_view,
    name="login"),

]