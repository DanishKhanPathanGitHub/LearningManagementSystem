from django.contrib.auth.backends import ModelBackend
from django.core.cache import cache

from ELearningApp import settings
from accounts.models import User
from django.db.models import Q, Count

class CachedUserBackend(ModelBackend):
    def get_user(self, user_id):
        cache_key = f"user_{user_id}"
        user = cache.get(cache_key)
        
        if not user:
            try:
                user = User.objects.select_related('userprofile').prefetch_related(
                    'userprofile__notifications').annotate(
                        unread_notifications_count=Count(
                            'userprofile__notifications', filter=Q(userprofile__notifications__read=False)
                        )).only(
                            'firstname', 'lastname', 'username', 'is_active', 'email', 'role', 'password',
                            'userprofile__profile_pic',
                             "userprofile__notifications__title", "userprofile__notifications__content", "userprofile__notifications__link", 
                             "userprofile__notifications__timestamp", "userprofile__notifications__assignment_id", "userprofile__notifications__read"
                        ).get(pk=user_id)
                cache.set(cache_key, user, timeout=180)
            except User.DoesNotExist:
                return None
        
        return user if self.user_can_authenticate(user) else None
