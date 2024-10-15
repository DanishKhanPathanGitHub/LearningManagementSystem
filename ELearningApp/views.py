from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from accounts.models import User, userProfile
from accounts.forms import userProfileForm, userMiniForm
from classroom.models import Classroom, Notification
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET

def home(request):
    try:
        user_profile = userProfile.objects.get(user=request.user)
        if user_profile.user.role == 1:
            classrooms = Classroom.objects.filter(students=user_profile)
        else:
            classrooms = Classroom.objects.filter(tutor=user_profile)
        
    except:
        classrooms=None
        user_profile=None

    context = {
        "classrooms":classrooms,
        "user_profile":user_profile,
    }
    return render(request, 'home.html', context)



@login_required(login_url='login')
def profile(request):
    user_profile = userProfile.objects.get(user=request.user)
    user_profile_form = userProfileForm(instance=user_profile)
    user_mini_form = userMiniForm(instance=user_profile.user)
    if request.POST:
        user_profile_form = userProfileForm(request.POST, request.FILES, instance=user_profile)
        user_mini_form = userMiniForm(request.POST, instance=request.user)
        if user_profile_form.is_valid() and user_mini_form.is_valid():
            user_mini = user_mini_form.save()
            
            user_profile = user_profile_form.save(commit=False)
            user_profile.user = user_mini  # Assuming request.user is the current logged-in user
            user_profile.save()
            messages.success(request, "user data updated")
            return redirect('/profile')
    try:
        if user_profile.user.role == 1:
            classrooms = Classroom.objects.filter(students=user_profile).count()
        else:
            classrooms = Classroom.objects.filter(tutor=user_profile).count()
    except:
        classrooms: 0
    context = {
        "user_profile":user_profile,
        "user_profile_form":user_profile_form,
        "user_mini_form":user_mini_form,
        "classroom_count":classrooms,
    }
    return render(request, 'profile.html', context)


@login_required(login_url='login')
def notifications(request):
    profile = userProfile.objects.get( user=request.user)

    # Fetch notifications for this user profile
    notis = Notification.objects.filter(user=profile).order_by("-timestamp")

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
        noti = Notification.objects.get(id=nid)
        if not noti.read:
            noti.read = True
            noti.save()
            return JsonResponse({'status':'success',})
        else:
            return JsonResponse({'status':'already seen'})
    except Notification.DoesNotExist:
        return JsonResponse({'status':'failure', 'message':'notification not found'})