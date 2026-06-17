from django.shortcuts import render, redirect
from .forms import RegistrationRequestForm, LoginForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
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


