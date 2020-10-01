from django.db import models

from django.contrib.auth.models import User

# Create your models here.

class Contribution(models.Model):
    waste_type = models.CharField(max_length=30)
    adress = models.CharField(max_length=50)
    photo_url = models.CharField(max_length=500)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, blank=True, null=True)
