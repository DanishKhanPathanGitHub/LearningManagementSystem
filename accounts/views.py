from django.shortcuts import render, redirect
from .forms import *
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import PermissionDenied
from .utils import check_role_tutor, check_role_student, send_verification_email
# Create your views here.

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError,ValueError, OverflowError ,User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Your account got activated')
        return redirect('login')
    else:
        print(user, token)
        messages.error(request, 'Activation link is not working! try again')
        return redirect('home')


def registerUser(request):
    if request.user.is_authenticated:
        messages.warning(request, 'you are already logged in')
        return redirect('myAccount')
    else:
        user_form = userForm()
        if request.POST:
            user_form = userForm(request.POST)
            if user_form.is_valid():
                password = user_form.cleaned_data['password']
                user = user_form.save(commit=False)
                user.set_password(password)
                user.save()
                #send verification email
                mail_subject = 'Activate your account'
                email_template = 'emails/account_verification.html'
                send_verification_email(request, user, mail_subject, email_template)
                messages.success(request, "Account verification link sent to your email, verify to login")
                return redirect('login')
        
        context ={
            "user_form": user_form
        }
        return render(request, 'accounts/registerUser.html', context)

def login(request):
    if request.user.is_authenticated:
        messages.warning(request, 'you are already logged in')
        return redirect('home')
    else:
        if request.POST:
            email = request.POST['email']
            password = request.POST['password']
            user = auth.authenticate(email=email, password=password)

            if user is not None:
                auth.login(request, user)
                messages.success(request, "You are now logged in")
                return redirect('home')
            else:
                messages.error(request, 'invalid login credentials')
                return redirect('login')
            
        return render(request, 'accounts/login.html')

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.info(request, 'you are logged out')
    return redirect('login')

def reset_password(request, uid):
    try:
        user=User.objects.get(pk=uid)
        if request.POST:
            password = request.POST['password']
            confirm_password = request.POST['confirm_password']
            print(password, confirm_password)
            if password == confirm_password and password:
                user.set_password(password)
                user.save()
                messages.success(request, 'password reset succesfully')
                return redirect('login')
            else:
                messages.error(request, "Passwords did't matched")
                return redirect('reset_password', uid=uid)
        return render(request, 'accounts/reset_password.html', {"uid":uid})
    except:
        return render(request, '404.html')

def reset_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError,ValueError, OverflowError ,User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid']=uid
        messages.info(request, 'Reset your password')
        return redirect('reset_password', uid=uid)
    else:
        messages.error(request, 'Activation link is not working! try again')
        return redirect('forgot_password')

def forgot_password(request):
    if request.POST:
        email = request.POST['email']
        if User.objects.filter(email=email):
            user = User.objects.get(email__exact=email)
            
            #send reset password verification
            mail_subject = 'Reset your password'
            email_template = 'emails/reset_password_validate.html'
            send_verification_email(request, user, mail_subject, email_template)
            messages.success(request, 'Password reset link sent to your email account')
            messages.success(request, 'verify and set new password to login')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist!')
            redirect('forgot_password')
    return render(request, 'accounts/forgot_password.html')