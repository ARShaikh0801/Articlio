from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class CustomUser(AbstractUser):
    """
    Custom user model for Articlio.
    Supports user roles (reader or author), email verification status,
    theme preferences, and profile completion checks for OAuth users.
    """
    ROLE_CHOICES = (
        ('reader', 'Reader'),
        ('author', 'Author'),
    )

    name=models.CharField(max_length=200)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='reader')
    verified=models.BooleanField(default=False)
    theme_preference = models.CharField(max_length=20, default='ocean')
    social_profile_completed = models.BooleanField(default=True)
    bio = models.TextField(max_length=500, blank=True)
    profile_picture_url = models.URLField(max_length=500, blank=True, default='')
    profile_picture = models.FileField(upload_to='profile_pics/', blank=True, null=True)
    github_url = models.URLField(max_length=200, blank=True, default='')
    twitter_url = models.URLField(max_length=200, blank=True, default='')
    linkedin_url = models.URLField(max_length=200, blank=True, default='')
    website_url = models.URLField(max_length=200, blank=True, default='')
    interests = models.TextField(blank=True, default='')
    onboarding_completed = models.BooleanField(default=True)  # True so existing users skip onboarding
    
    def __str__(self):
        return self.username

class Follow(models.Model):
    follower = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='following_relations')
    followed = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='follower_relations')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'followed')

    def __str__(self):
        return f"{self.follower.username} follows {self.followed.username}"


@receiver(post_save, sender=CustomUser)
def update_bloom_filter_on_user_save(sender, instance, created, **kwargs):
    """
    Signal handler: whenever a user is created or updated, we add their 
    username to the cached Bloom Filter to keep it synchronized.
    """
    try:
        from home.utils import get_username_bloom_filter
        from django.core.cache import cache
        
        bf = get_username_bloom_filter()
        bf.add(instance.username.lower())
        # Update the cache with the newly modified Bloom Filter
        cache.set('username_bloom_filter', bf, timeout=None)
    except Exception as e:
        # If cache/filter fails for any reason, don't break the user save process
        print(f"Error updating bloom filter: {e}")

class Contact(models.Model):
    """
    Model representing contact form submissions from users.
    Stores name, email, phone, message content, and submission timestamp.
    """
    sno=models.AutoField(primary_key=True)
    name=models.CharField(max_length=200)
    email=models.CharField(max_length=200)
    phone=models.CharField(max_length=13)
    content=models.TextField()
    timestamp=models.DateTimeField(auto_now_add=True,blank=True)

    def __str__(self):
        return self.name

class Visitor(models.Model):
    """
    Tracks unique site visitors using a long-lived cookie.
    """
    visitor_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.visitor_id