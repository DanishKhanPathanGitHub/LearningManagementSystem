from collections import defaultdict
from django.utils import timezone
import datetime
from django.core.exceptions import ValidationError
from django.shortcuts import render
from .models import Classroom, Assignment, Announcement, Lecture, Section, StudentClassroom, StudentLectureProgress
from accounts.utils import image_validator
import os
from django.core import cache
from django.db.models import Q, Prefetch, Count
    
def check_classroom_participant(user, id, use_cache=True):
    is_participant = False
    if use_cache == True:
        cache_key = f"classroom_participant_{user.id}_{id}"
        is_participant = cache.cache.get(cache_key)

        if is_participant is None:
            is_participant = Classroom.objects.only('id').filter(
                Q(tutor=user.userprofile) | Q(students=user.userprofile),
                id=id
            ).exists()
            cache.cache.set(cache_key, is_participant, timeout=180)  
    else:
        is_participant = Classroom.objects.only('id').filter(
            Q(tutor=user.userprofile) | Q(students=user.userprofile),
            id=id
        ).exists()

    return is_participant   
    
def file_validator(value):
    extention = os.path.splitext(value.name)[1]
    valid_extentions = ['.pdf', '.doc', '.docx', '.ppt', '.pptx',]
    print('file type got chcekd')
    if not extention.lower() in valid_extentions:
        raise ValidationError('Unsupported file type, upload supported file type: '+ str(valid_extentions))
    max_size = 5 * 1024 * 1024  # 5MB in bytes
    print('value size: ', value.size)
    print('max size: ', max_size)
    if value.size > max_size:
        raise ValidationError('File size exceeds the maximum limit of 5MB.')
    
def video_file_validator(value):
    extention = os.path.splitext(value.name)[1]
    valid_extentions = ['.mp4', '.webm']
    print('file type got chcekd')
    if not extention.lower() in valid_extentions:
        raise ValidationError('Unsupported file type, upload supported file type: '+ str(valid_extentions))
    max_size = 20 * 1024 * 1024  # 20MB in bytes
    print('value size: ', value.size)
    print('max size: ', max_size)
    if value.size > max_size:
        raise ValidationError('File size exceeds the maximum limit of 20MB.')
    
def combine_file_validator(value):
    try:
        file_validator(value)
    except ValidationError as e1:
        try:
            image_validator(value)
        except ValidationError as e2:
            raise ValidationError(e1, e2)
        


def load_class_data_from_cache(request, user_id, id):
    """
    This will load the data from the cache if exist,
    if not then set the data into cache and will load
    if class data exist, and also cache reload key set to True and with time,
    then it will check if the last reload of the class data is > time at which reload key set,
    if so, then it will return class data, and if not, 
    then it means reload key is valid for the user & that's why user needs to reload the class data
    
    there is 3 type of caches here in use:
    
    class_data: 
    -----------
        type: dict
        unique for each user for each classroom, 
        contains 'last_reload' key with datetime object value, which represents the datetime object at which class_data got reloaded last time
    
    cache_reload_all_data, reload_all_at:
    -------------------------------------
        unique for each classroom, same for users within classroom
        cache_reload_all_data is boolean type, represents if reload is required or not
        reload_all_at is datetime object, represents the time, from which reload is required

    cache_reload_student, reload_student_at:
        same as above but for student user only
 
    """
    try:
        cache_key = f'{user_id}_class_{id}_data'
        class_data = cache.cache.get(cache_key)
        
        cache_reload_student = False
        cache_reload_all_data, reload_all_at = cache.cache.get(key=f'cache_reload_{id}_all', default=(None, None))   

        if request.user.role == 1:
            cache_reload_student, reload_student_at = cache.cache.get(f'cache_reload_{id}_student', default=(None, None))
        
        if class_data:
            if cache_reload_all_data:
                if reload_all_at and class_data['last_reload'] > reload_all_at: #9:00:40 > 9:00:30
                    return class_data
                
            elif cache_reload_student:
                if reload_student_at and class_data['last_reload'] > reload_student_at:
                    return class_data
            else:
                return class_data

        new_class_data = defaultdict()
        
        Class = Classroom.objects.prefetch_related(
            Prefetch(
                'assignments',
                queryset=Assignment.objects.order_by('-assigned_date')
            ),
            Prefetch(
                'announcements',
                queryset=Announcement.objects.order_by('-upload_date')
            )
        ).select_related('tutor').only(
            'name', 'description', 'cover_pic', 'created_at', 'tutor_id'
        ).annotate(
            students_count=Count('students')
        ).get(id=id)

        new_class_data['class'] = Class

        sections = Section.objects.filter(classroom__id=id).only('id', 'title', 'order').order_by('order').prefetch_related(
            Prefetch(
                'lectures',
                queryset=Lecture.objects.only('id', 'title', 'order', 'slug', 'section__id').order_by('order'),
            )
        )
        new_class_data['sections'] = sections
        new_class_data['last_reload'] = timezone.now()

        cache.cache.set(cache_key, new_class_data, timeout=180)
        
        return new_class_data
        
    except Exception as e:
        print(e)
        return render(request, '404.html')
    