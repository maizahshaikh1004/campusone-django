from django.urls import path,include
from . import views
from academics import views as academics_views

urlpatterns = [
    path('',views.home,name='home'),
    path('student/dashboard/',views.student_dashboard,name="student_dashboard"),
    path('faculty/dashboard/',views.faculty_dashboard,name="faculty_dashboard"),
    path('admin/', views.admin_redirect, name='admin_redirect'),
    path('admin/dashboard/',views.admin_dashboard,name="admin_dashboard"),
    path('admin/students/', views.admin_students_list, name='admin_students_list'),
    path('admin/faculty/', views.admin_all_faculty, name='admin_all_faculty'),
    path('admin/events/', views.admin_events, name='admin_events'),
    path('admin/notices/', views.admin_notices, name='admin_notices'),
    path('admin/bulk-upload/', views.bulk_user_upload, name='bulk_user_upload'),
    path('admin/timetable/', views.admin_timetable, name='admin_timetable'),
    path('admin/attendance-report/', views.admin_attendance_report, name='admin_attendance_report'),
    path('admin/corrections/', views.attendance_corrections_admin, name='attendance_corrections_admin'),
    path('admin/corrections/approve/<int:request_id>/', views.approve_attendance_correction_view, name='approve_attendance_correction'),
    path('admin/corrections/reject/<int:request_id>/', views.reject_attendance_correction_view, name='reject_attendance_correction'),
    path('admin/users/toggle/<int:profile_id>/', views.toggle_user_status_view, name='toggle_user_status'),
    path("",include("users.urls")),
    
    # Global AJAX paths used in templates
    path('ajax/get-semesters/', academics_views.get_semesters_by_department, name='get_semesters_by_department'),
    path('ajax/get-classes/', academics_views.get_classes_by_department, name='get_classes_by_department'),
    path('ajax/get-semesters-by-class/', academics_views.get_semesters_by_class, name='get_semesters_by_class'),
    path('ajax/get-subjects-by-semester/', academics_views.get_subjects_by_semester, name='get_subjects_by_semester'),
    path('ajax/get-subjects-by-class/', academics_views.get_subjects_by_class, name='get_subjects_by_class'),
    path('ajax/get-timetable-slots/', academics_views.get_timetable_slots, name='get_timetable_slots'),
]
