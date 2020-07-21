from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

# create models
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    description = models.TextField(max_length=300, blank=True)
    location = models.CharField(max_length=30, blank=True)
    phone = models.IntegerField(blank=True)

def __str__(self):
            return self.user.username

def create_profile(sender, **kwargs):
    if kwargs['created']:
        user_profile = UserProfile.objects.create(user=kwargs['instance'])

post_save.connect(create_profile, sender=User)



