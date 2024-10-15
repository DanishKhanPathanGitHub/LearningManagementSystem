from django.urls import path
from . import views

urlpatterns = [
    path('registerUser/', views.registerUser, name='registerUser'),

    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),

    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('reset_password/<uid>', views.reset_password, name='reset_password'),
    path('reset_password_validate/<uidb64>/<token>', views.reset_password_validate, name='reset_password_validate'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
]

