from django.urls import path
from . import views

urlpatterns = [
    path("student/notices/",views.student_notices, name="student_notices"),
    path("student/events/",views.student_events, name="student_events"),
    path("event/<int:event_id>/",views.event_detail, name="event_detail"),
]
