from django.contrib.auth.models import User
from users.models import Profile

class ProfileCreationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                # Access the profile to trigger the DoesNotExist exception if it's missing
                _ = request.user.profile
            except Profile.DoesNotExist:
                role = 'ADMIN' if request.user.is_superuser else 'STUDENT'
                Profile.objects.create(
                    user=request.user,
                    role=role,
                    full_name=request.user.username.title()
                )
        return self.get_response(request)
