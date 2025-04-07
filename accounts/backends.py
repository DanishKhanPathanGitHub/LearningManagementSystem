from django.contrib.auth.backends import ModelBackend
from django.core.cache import cache

from ELearningApp import settings
from accounts.models import User
from django.db.models import Q, Count
from django.utils import timezone

class CachedUserBackend(ModelBackend):
    def get_user(self, user_id):
        cache_key = f"user_{user_id}"
        user, last_reload_at = cache.get(key=cache_key, default=(None, None))
        
        if not user: 
            try:
                user = User.objects.select_related('userprofile').only(
                            'firstname', 'lastname', 'username', 'is_active', 'email', 'role', 'password',
                            'userprofile__profile_pic',
                        ).get(pk=user_id)
                cache.set(cache_key, (user, timezone.now()), timeout=180)
            except User.DoesNotExist:
                return None
        
        
        return user if self.user_can_authenticate(user) else None
