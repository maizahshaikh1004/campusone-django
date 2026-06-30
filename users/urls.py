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
    path("logout/",views.logout_view,name="logout"),
    path("profile/",views.profile,name="profile"),
    path("profile/<int:profile_id>/",views.view_profile,name="view_profile"),
    path("profile/edit/",views.edit_profile, name="edit_profile"),
    path("admin/registrations/", views.admin_registration_requests_view, name="admin_registration_requests"),
    path("admin/registrations/approve/<int:request_id>/", views.approve_registration_view, name="approve_registration"),
    path("admin/registrations/reject/<int:request_id>/", views.reject_registration_view, name="reject_registration"),
]