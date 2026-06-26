from django.urls import path
from . import views

urlpatterns = [
    path("student/notices/",views.student_notices, name="student_notices"),
    path("student/events/",views.student_events, name="student_events"),
    path("event/<int:event_id>/",views.event_detail, name="event_detail"),
    path('student/attendance/', views.student_attendance, name='student_attendance'),
    path('student/attendance/<int:subject_id>/', views.student_attendance_detail, name='student_attendance_detail'),
    path('student/subjects/',views.student_subjects,name="student_subjects"),
    path('student/timetable/',views.student_timetable,name="student_timetable"),
    path("student/coordinator-events/",views.student_coordinator_events,name="student_coordinator_events"),
    path("student/past-coordinator-events/",views.student_past_coordinator_events,name="student_past_coordinator_events"),
    
]
