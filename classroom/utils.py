from django.core.exceptions import PermissionDenied, ValidationError
from .models import Classroom
from accounts.models import userProfile, User
from accounts.utils import image_validator
import os

def check_classroom_participant(user, id):
    user_profile = userProfile.objects.get(user=user)
    try:    
        try:
            classroom = Classroom.objects.get(tutor=user_profile, id=id)
            if classroom:
                return True
            else:
                return False
        except:
            classroom = Classroom.objects.get(students=user_profile, id=id)
            if classroom:
                return True
            else:
                return False
    except:
        raise PermissionDenied       
    
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