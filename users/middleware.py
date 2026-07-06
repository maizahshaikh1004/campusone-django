from django.contrib.auth.models import User
from users.models import Profile

class ProfileCreationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                profile = request.user.profile
                # Auto-heal: If user is superuser but role is not ADMIN, update it
                if request.user.is_superuser and profile.role != 'ADMIN':
                    profile.role = 'ADMIN'
                    profile.save()
            except Profile.DoesNotExist:
                role = 'ADMIN' if request.user.is_superuser else 'STUDENT'
                Profile.objects.create(
                    user=request.user,
                    role=role,
                    full_name=request.user.username.title()
                )
        return self.get_response(request)
