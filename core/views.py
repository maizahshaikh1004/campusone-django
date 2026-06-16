from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from academics.models import Subject

def home(request):
    return render(request,'home.html')

@login_required
def student_dashboard(request):
    #profile=request.user.profile
    #context={"name": request.user.username}

    return render(
        request,
        "student/dashboard.html"
        #context
    )