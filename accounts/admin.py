from django.contrib import admin
from accounts.models import User, userProfile

from django.contrib.auth.admin import UserAdmin
# Register your models here.
class customUserAdmin(UserAdmin):
    list_display = ('firstname','lastname','username','email','role','is_active')
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
    ordering = ('-date_joined',)

admin.site.register(User, customUserAdmin)
admin.site.register(userProfile)