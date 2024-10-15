from datetime import timedelta
from django.utils import timezone
from typing import Any
from classroom.models import Classroom
from django import forms
from .models import *
from classroom.models import Assignment
from tinymce.widgets import TinyMCE


class ClassroomForm(forms.ModelForm):
    cover_pic = forms.ImageField(widget=forms.FileInput())
    class Meta:
        model = Classroom
        fields = ("name", "cover_pic", "code", "password",)

    def clean(self):
        cleaned_data = super(ClassroomForm, self).clean()
        code = cleaned_data.get('code')
        password = cleaned_data.get('password')

        if code and password:
            try:
                Classroom.objects.get(code=code, password=password)
                raise forms.ValidationError("A classroom with this code and password already exists.")
            except Classroom.DoesNotExist:
                if len(code)<6:
                    raise forms.ValidationError("code must be minimum 6 character long")
                if len(password)<8:
                    raise forms.ValidationError("password must be minimum 6 character long")

class ClassroomMiniForm(forms.ModelForm):
    description = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}))
    class Meta:
        model = Classroom
        fields = ("description", "name", "cover_pic")

    def clean_description(self):
        description = self.cleaned_data["description"]
        if not description:
            raise forms.ValidationError("description can't be blank")
        return description   
    


class AssignmentUpdateForm(forms.ModelForm):
    due_date = forms.DateTimeField(required=False, widget=forms.DateTimeInput(attrs={"type": "datetime-local"}))
    late_submission_allow = forms.BooleanField(required=False)
    class Meta:
        model = Assignment
        fields = ("due_date","late_submission_allow",)
    
    def clean_due_date(self):
        due_date = self.cleaned_data['due_date']
        if due_date and due_date <= timezone.now():
            raise forms.ValidationError("Due date must be ahead of current time")        
        return due_date