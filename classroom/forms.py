from datetime import timedelta
from typing import Any
from classroom.models import *
from django import forms
from .models import *
from .utils import *
from django.core.validators import FileExtensionValidator
from django.utils import timezone
from tinymce.widgets import TinyMCE
import uuid
from django.utils.text import slugify

class AssignmentForm(forms.ModelForm):
    assignment=forms.FileField(widget=forms.FileInput(attrs={"class":"btn-btn-info"}), validators=[file_validator])
    due_date = forms.DateTimeField(widget=forms.DateTimeInput(attrs={"type": "datetime-local"}))
    class Meta:
        model = Assignment
        fields = ("assignment", "name", "description", "due_date", "late_submission_allow",)

    def clean_due_date(self):
        due_date = self.cleaned_data['due_date']
        if due_date <= timezone.now() + timedelta(hours=24):
            raise forms.ValidationError("Due date must be 24 hours from current time")
        return due_date

class AssignmentSubmissionForm(forms.ModelForm):
    submitted_file=forms.FileField(widget=forms.FileInput(attrs={"class":"btn-btn-info"}), validators=[file_validator])
    class Meta:
        model = AssignmentSubmission
        fields = ("submitted_file",)
        

class AnnouncementForm(forms.ModelForm):
    file=forms.FileField(widget=forms.FileInput(attrs={"class":"btn-btn-info"}), validators=[combine_file_validator], required=False)
    class Meta:
        model = Announcement
        fields = ("title", "content", "file", "link",)


class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ("title", "order",)
        labels = {
            'title': 'Title of Section...',
        }

    def __init__(self, *args, classroom=None, is_update=False, **kwargs):
        super().__init__(*args, **kwargs)
        max_order = Section.objects.filter(classroom=classroom).aggregate(Max('order'))['order__max'] or 0
        if is_update:
            max_order -= 1 
        # Create choices for the order field
        self.fields['order'] = forms.ChoiceField(
            choices=[(i, str(i)) for i in range(max_order + 1, 0, -1)],
            widget=forms.Select(attrs={'class': 'form-control'}),  # Add any classes or attributes as needed
            label='order of the section | If you select x, sections from x onwards will move ahead. Ex. If you select 3, existing sections from 3 would be 4, 5, and so on.'
        )

class LectureForm(forms.ModelForm):
    class Meta:
        model = Lecture
        fields = ['order', 'attachment', 'video', 'content', 'title', 'slug', 'section']
        
    def __init__(self, *args, section=None, **kwargs):
        super().__init__(*args, **kwargs)

        is_update = self.instance.pk is not None

        max_order = Lecture.objects.filter(section=section).aggregate(Max('order'))['order__max'] or 0
        # Create choices for the order field
        if not is_update and section:
            self.fields['section'].required = False

            self.fields['order'] = forms.ChoiceField(
                choices=[(i, str(i)) for i in range(max_order+1, 0, -1)],
                widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select order...'}),  # Add any classes or attributes as needed
                label='order of the lecture | If you select x, lectures of cuurent section from x onwards will move ahead. Ex. If you select 3, existing lectures from 3 would be 4, 5, and so on.\
                    by default it will be added as last lecture in the section'
            )

        elif is_update and section:
            self.fields['section'].initial = section
            self.fields['section'].queryset = Section.objects.filter(classroom=section.classroom)
        
        self.fields['content'] = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}), required=False)
        self.fields['attachment'] = forms.FileField(
            widget=forms.FileInput(attrs={"class":"btn-btn-info"}), 
            validators=[combine_file_validator],
            required=False
        )
        self.fields['video'] = forms.FileField(
            widget=forms.FileInput(attrs={"class":"btn-btn-info"}),
            validators=[video_file_validator],
            required=False
        )
        self.fields['slug'] = forms.SlugField(
            widget=forms.HiddenInput(),
            required=False
        )   

    def clean(self):
        cleaned_data = super().clean()
        
        video = cleaned_data.get('video')
        content = cleaned_data.get('content')
        if content or video:
            pass
        else:
            raise forms.ValidationError("Lecture should have atleast either content or video")

        old_video = self.instance.video
        old_attachment = self.instance.attachment

        new_video = cleaned_data.get('video')
        new_attachment = cleaned_data.get('attachment')

        if new_video and old_video != new_video:
            if old_video:
                old_video.delete(save=False)

        if new_attachment and old_attachment != new_attachment:
            if old_attachment:
                old_attachment.delete(save=False)

        title = cleaned_data.get('title')
        uid = str(uuid.uuid4())
        slug = slugify(f"{title}-{uid[:8]}")
        cleaned_data['slug'] = slug

class CommentForm(forms.ModelForm):
    
    class Meta:
        model = Comment
        fields = ("text","image",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['text'] = forms.CharField(
            widget=TinyMCE(attrs={'cols': 40, 'rows': 20}), required=True
        )
        self.fields['image'] = forms.FileField(
            widget=forms.FileInput(attrs={"class":"btn-btn-info"}),
            validators=[image_validator],
            required=False
        )