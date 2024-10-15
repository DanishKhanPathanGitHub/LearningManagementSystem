from accounts.models import userProfile

def get_user_profile(request):
    user_profile = None
    if request.user.is_authenticated:
        try:
            user_profile = userProfile.objects.get(user=request.user)
        except userProfile.DoesNotExist:
            pass
    return {'user_profile': user_profile}