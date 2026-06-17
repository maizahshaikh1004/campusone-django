from django.contrib import admin
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Profile, RegistrationRequest
# Register your models here.
@admin.action(description="Approve selected registration requests")
def approve_requests(modeladmin, request,queryset):
    for registration in queryset:
        if registration.status!="PENDING":
            continue
        base_username=(registration.name.lower().replace(" ",""))
        username=base_username
        counter=1
        while User.objects.filter(username=username).exists():
            username=f"{base_username}{counter}"
            counter+=1
        user=User.objects.create(
            username=username,
            email=registration.email,
            is_active=False,
        )
        profile = user.profile

        profile.full_name = registration.name
        profile.role = registration.role
        profile.department = registration.department
        profile.academic_class = registration.academic_class

        profile.save()
        registration.status="APPROVED"
        registration.reviewed_at = timezone.now()
        registration.save()

@admin.action(description="Reject selected registration requests")
def reject_requests(modeladmin, request, queryset):
    for registration in queryset:
        if registration.status != "PENDING":
            continue
        registration.status = "REJECTED"
        registration.reviewed_at = timezone.now()

        registration.save()        

@admin.register(RegistrationRequest)
class RegistrationRequestAdmin(admin.ModelAdmin):
    list_display=(
        "name",
        "email",
        "role",
        "status",
        "requested_at"
    )
    list_filter=(
        "status",
        "role"
    )
    actions=[approve_requests,
    reject_requests]
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display=(
        "full_name",
        "role",
        "department"
    )
