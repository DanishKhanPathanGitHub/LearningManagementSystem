from accounts.models import userProfile
from classroom.models import Notification

def get_notification_count(request):
    notification_count = 0
    if request.user.is_authenticated:
        try:
            user_profile = userProfile.objects.get(user=request.user)
            notification_count = Notification.objects.filter(user=user_profile, read=False).count()
        except:
            pass
    return {'notification_count':notification_count}
