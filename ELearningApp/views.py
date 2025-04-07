from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from accounts.models import User, userProfile
from accounts.forms import userProfileForm, userMiniForm
from classroom.models import Classroom, Notification
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from django.db.models import Q
from django.core import cache
from django.utils import timezone

def home(request):
    try:
        classrooms = Classroom.objects.filter(
            Q(students=request.user.userprofile)|Q(tutor=request.user.userprofile)
        ).select_related('tutor__user').only(
            'cover_pic', 'name', 'created_at', 'tutor__user__username', 'tutor__profile_pic'
        ).distinct()

    except:
        classrooms=None

    context = {
        "classrooms":classrooms,
    }
    return render(request, 'home.html', context)



@login_required(login_url='login')
def profile(request):
    user_profile_form = userProfileForm(instance=request.user.userprofile)
    user_mini_form = userMiniForm(instance=request.user)
    classrooms = 0
    if request.POST:
        user_profile_form = userProfileForm(request.POST, request.FILES, instance=request.user.userprofile)
        user_mini_form = userMiniForm(request.POST, instance=request.user)
        if user_profile_form.is_valid() and user_mini_form.is_valid():
            user_mini = user_mini_form.save()
            
            user_profile = user_profile_form.save(commit=False)
            user_profile.user = user_mini
            user_profile.save()
            messages.success(request, "user data updated")
            return redirect('/profile')
    try:
        if user_profile.user.role == 1:
            classrooms = Classroom.objects.only('id').filter(students=request.user.userprofile).count()
        else:
            classrooms = Classroom.objects.only('id').filter(tutor=request.user.userprofile).count()
    except:
        pass
    context = {
        "user_profile":request.user.userprofile,
        "user_profile_form":user_profile_form,
        "user_mini_form":user_mini_form,
        "classroom_count":classrooms,
    }
    return render(request, 'profile.html', context)


@login_required(login_url='login')
def notifications(request):

    # Fetch notifications for this user profile
    notis = request.user.userprofile.notifications.order_by("-timestamp")

    if request.GET:
        filter = request.GET.get('filter')
        if filter == "seen":
            notis = notis.filter(read=True)
    
        if filter == "unread":
            notis = notis.filter(read=False)

    # Context to be passed to the template
    context = {
        "notis": notis,
    }

    return render(request, 'notifications.html', context)

@login_required(login_url='login')
@require_GET
def mark_notification_as_read(request, nid):
    try:
        noti = Notification.objects.only('id', 'read').get(id=nid)
        if not noti.read:
            noti.read = True
            cache_key = f'user_{request.user.id}'
            user, last_reload_at = cache.cache.get(cache_key, default=None)
            if user:
                user.unread_notifications_count -= 1
                cache.cache.set(cache_key, (user, timezone.now()), timeout=180)
            noti.save()
            return JsonResponse({'status':'success',})
        else:
            return JsonResponse({'status':'already seen'})
    except Notification.DoesNotExist:
        return JsonResponse({'status':'failure', 'message':'notification not found'})
    
