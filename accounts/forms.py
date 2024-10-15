from django import forms
from .models import *
from accounts.utils import image_validator

class userForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = User
        fields = ("firstname", "lastname", "username", "email", "password","role",)

    def clean(self):
        cleaned_data = super(userForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        
        if password and len(password)<8:
            raise forms.ValidationError('Password must be atleast 8 characters long')

class userMiniForm(forms.ModelForm):
    
    class Meta:
        model = User
        fields = ("firstname", "lastname", "username",)


class userProfileForm(forms.ModelForm):
    profile_pic=forms.ImageField(widget=forms.FileInput(attrs={"class":"btn-btn-info"}), validators=[image_validator], required=False)
    class Meta:
        model = userProfile
        fields = ["profile_pic",]

