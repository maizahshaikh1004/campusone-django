from django.urls import path,include
from . import views

urlpatterns = [
    path('',views.home,name='home'),
    path('student/dashboard/',views.student_dashboard,name="student_dashboard"),
    path('faculty/dashboard/',views.faculty_dashboard,name="faculty_dashboard"),
    path("",include("users.urls")),


]
