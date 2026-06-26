from django.urls import path
from . import views

urlpatterns = [
    path("student/assignments/",views.student_assignments,name="student_assignments"),
    path("student/assignments/<int:assignment_id>/",views.submit_assignment,name="submit_assignment"),
    

]
