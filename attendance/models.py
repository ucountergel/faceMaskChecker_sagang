from multiprocessing.spawn import old_main_modules
from statistics import mode
from unicodedata import category
from django.db import models
from django.contrib.auth.models import User

from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name='profile')
    contact = models.CharField(max_length=250)
    dob = models.DateField(blank=True, null = True)
    address = models.TextField(blank=True, null = True)
    avatar = models.ImageField(blank=True, null = True, upload_to= 'images/')
    user_type = models.IntegerField(default = 2)
    gender = models.CharField(max_length=100, choices=[('Male','Male'),('Female','Female')], blank=True, null= True)
    users_types = models.CharField(max_length=255)
    cam = models.CharField(max_length=255)
    Assigned_places = models.CharField(max_length=255)
    SystemName = models.CharField(max_length=255)
    gmail = models.CharField(max_length=255)



    def __str__(self):
        return self.user.username
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    print(instance)
    try:
        profile = UserProfile.objects.get(user = instance)
    except Exception as e:
        UserProfile.objects.create(user=instance)
    instance.profile.save()
