from django.urls import path
from . import views

urlpatterns = [
    path("student/assignments/",views.student_assignments,name="student_assignments"),
    path("student/assignments/<int:assignment_id>/",views.submit_assignment,name="submit_assignment"),
    path("assignments/",views.faculty_assignments,name="faculty_assignments"),
    path("submissions/",views.faculty_submissions,name="faculty_submissions"),
    path("assignments/create/",views.create_assignment,name="create_assignment"),
    path("assignments/<int:assignment_id>/edit/",views.edit_assignment,name="edit_assignment"),
    path("<int:assignment_id>/delete/",views.delete_assignment,name="delete_assignment"),

]
