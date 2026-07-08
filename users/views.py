from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistrationRequestForm, LoginForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import RegistrationRequest, Profile
from django.core.mail import send_mail
from django.conf import settings

def register_request(request):
    if request.method=="POST":
        form=RegistrationRequestForm(request.POST)
        
        if form.is_valid():
            form.save()
            return render(
                request, "users/registration_success.html"
            )
    else:
        form=RegistrationRequestForm()
    return render(
        request, 
    "users/register.html",
    {
        "form":form
        }
    )

def set_password(request, user_id):
    user=User.objects.get(id=user_id)

    if request.method=='POST':
        password=request.POST.get("password")
        confirm_password=request.POST.get("confirm_password")

        if password != confirm_password:
            return render(
                "users/set_password.html",
                {"error":"Passwords do not match."}
            )
        user.set_password(password)
        user.is_active=True
        user.save()

        return redirect("home")

    return render(
        request,
        "users/set_password.html"
    )

def login_view(request):
    form=LoginForm()
    if request.method == "POST":
        form=LoginForm(request.POST)

        if form.is_valid():
            username=form.cleaned_data["username"]
            password=form.cleaned_data["password"]
            user=authenticate(request, username=username,password=password)

            if user is not None:
                login(request,user)
                if user.is_superuser:
                    return redirect("/admin/")
                profile=user.profile
                if profile.role=="ADMIN":
                    return redirect("admin_dashboard")
                elif profile.role=="FACULTY":
                    return redirect("faculty_dashboard")
                elif profile.role=="STUDENT":
                    return redirect("student_dashboard")
            
            return render(
                request,
                "users/login.html",
                {
                    "form":form,
                    "error":"Invalid username or password."
                }
            )
    return render(
        request,
        "users/login.html",
        {"form":form}
    )

def logout_view(request):
    logout(request)
    return redirect("login")

@login_required
def profile(request):

    profile = request.user.profile

    return render(
        request,
        "users/profile.html",
        {
            "profile": profile
        }
    )

@login_required
def view_profile(request, profile_id):

    if request.user.profile.role != "ADMIN":
        return render(
            request,
            "403.html",
            {"message": "Admins Only"},
            status=403
        )

    profile = get_object_or_404(
        Profile.objects.select_related(
            "user",
            "department",
            "academic_class"
        ),
        pk=profile_id
    )

    return render(
        request,
        "users/view_profile.html",
        {
            "profile": profile
        }
    )


@login_required
def edit_profile(request):

    profile = request.user.profile

    if request.method == "POST":

        phone = request.POST.get("phone", "").strip()
        address = request.POST.get("address", "").strip()
        bio = request.POST.get("bio", "").strip()

        if phone:
            if (not phone.isdigit()) or len(phone) != 10:
                messages.error(
                    request,
                    "Phone number must contain exactly 10 digits."
                )
                return redirect("edit_profile")

        profile.phone = phone
        profile.address = address
        profile.bio = bio

        if "profile_photo" in request.FILES:
            profile.profile_photo = request.FILES["profile_photo"]

        profile.save()

        messages.success(
            request,
            "Profile updated successfully."
        )

        return redirect("profile")

    return render(
        request,
        "users/edit_profile.html",
        {
            "profile": profile
        }
    )


@login_required
def admin_registration_requests_view(request):
    if request.user.profile.role != 'ADMIN':
        return render(request, '403.html', {'message': 'Admins Only.'}, status=403)

    role_filter = request.GET.get('role', '')
    sort_order = request.GET.get('sort', 'desc')

    requests_qs = RegistrationRequest.objects.filter(status='PENDING')

    if role_filter in ['STUDENT', 'FACULTY']:
        requests_qs = requests_qs.filter(role=role_filter)

    if sort_order == 'asc':
        requests_qs = requests_qs.order_by('requested_at')
    else:
        requests_qs = requests_qs.order_by('-requested_at')

    return render(request, 'admin/admin_registration_requests.html', {
        'requests': requests_qs,
        'selected_role': role_filter,
        'selected_sort': sort_order,
    })


@login_required
def approve_registration_view(request, request_id):
    if request.user.profile.role != 'ADMIN':
        return render(request, '403.html', {'message': 'Admins Only.'}, status=403)

    req = get_object_or_404(RegistrationRequest, pk=request_id, status='PENDING')

    base_username = req.name.lower().replace(" ", "")
    username = base_username
    counter = 1
    while User.objects.filter(username=username).exists():
        username = f"{base_username}{counter}"
        counter += 1

    # Create user as inactive
    user = User.objects.create(
        username=username,
        email=req.email,
        is_active=False
    )
    profile = user.profile
    profile.full_name = req.name
    profile.role = req.role
    profile.department = req.department
    profile.academic_class = req.academic_class
    profile.save()

    # Mark signup request approved
    req.status = 'APPROVED'
    req.reviewed_at = timezone.now()
    req.save()

    try:
        subject = "CampusOne Account Activation & Password Setup"
        domain = request.get_host()
        protocol = "https" if request.is_secure() else "http"
        activation_link = f"{protocol}://{domain}/set-password/{user.id}/"
        message = (
            f"Dear {req.name},\n\n"
            f"Your registration request for the role of {req.role.title()} has been approved.\n"
            f"Please click the following link to set your password and activate your account:\n"
            f"{activation_link}\n\n"
            f"Best regards,\n"
            f"CampusOne Administration"
        )
        send_mail(
            subject,
            message,
            'noreply@campusone.com',
            [req.email],
            fail_silently=True
        )
        messages.success(request, f"Request approved. Activation email sent to {req.email}.")
    except Exception as e:
        messages.warning(request, f"Request approved, but failed to send activation email: {str(e)}")

    return redirect('admin_registration_requests')


@login_required
def reject_registration_view(request, request_id):
    if request.user.profile.role != 'ADMIN':
        return render(request, '403.html', {'message': 'Admins Only.'}, status=403)

    req = get_object_or_404(RegistrationRequest, pk=request_id, status='PENDING')
    req.status = 'REJECTED'
    req.reviewed_at = timezone.now()
    req.save()

    messages.success(request, f"Registration request for {req.name} has been rejected.")
    return redirect('admin_registration_requests')


def register_admin(request):
    if request.method == 'POST':
        name = request.POST.get("name")
        email = request.POST.get("email")
        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        invite_code = request.POST.get("invite_code")

        if not all([name, email, username, password, confirm_password, invite_code]):
            messages.error(request, "All fields are required.")
            return render(request, "users/register_admin.html")

        if invite_code != settings.ADMIN_SIGNUP_SECRET:
            messages.error(request, "Invalid invite code.")
            return render(request, "users/register_admin.html")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "users/register_admin.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, "users/register_admin.html")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return render(request, "users/register_admin.html")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_active=True,
            is_staff=True,
            is_superuser=True
        )

        profile = user.profile
        profile.full_name = name
        profile.role = "ADMIN"
        profile.save()

        messages.success(request, "Administrator account created successfully! You can now log in.")
        return redirect("login")

    return render(request, "users/register_admin.html")