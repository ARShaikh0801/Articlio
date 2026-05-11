from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('reader', 'Reader'),
        ('author', 'Author'),
    )

    name=models.CharField(max_length=200)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='reader')
    verified=models.BooleanField(default=False)
    theme_preference = models.CharField(max_length=20, default='ocean')
    
    def __str__(self):
        return self.username

# Create your models here.
class Contact(models.Model):
    sno=models.AutoField(primary_key=True)
    name=models.CharField(max_length=200)
    email=models.CharField(max_length=200)
    phone=models.CharField(max_length=13)
    content=models.TextField()
    timestamp=models.DateTimeField(auto_now_add=True,blank=True)

    def __str__(self):
        return self.name