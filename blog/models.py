from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()
from django.utils.timezone import now

class Post(models.Model):
    """
    Represents a blog post. Tracks metadata such as views, likes, category, 
    and draft status.
    """
    sno=models.AutoField(primary_key=True)
    title=models.CharField(max_length=200)
    content=models.TextField()
    summary = models.TextField(max_length=200, blank=True)
    author=models.CharField(max_length=100)
    slug=models.CharField(max_length=100,unique=True)
    category=models.CharField(max_length=200, default="general")
    views=models.IntegerField(default=0,editable=False)
    timestamp=models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes=models.IntegerField(default=0,editable=False)
    draft=models.BooleanField(default=False)

    def __str__(self):
        return self.title + ' ' + self.author
    
class BlogComment(models.Model):
    """
    Represents a comment or nested reply left on a blog post.
    """
    sno=models.AutoField(primary_key=True)
    comment=models.TextField()
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    post=models.ForeignKey(Post,on_delete=models.CASCADE)
    parent=models.ForeignKey('self',on_delete=models.CASCADE,null=True)
    timestamp=models.DateTimeField(default=now)

    def __str__(self):
        return self.comment[0:13]+"... by "+self.user.username
    
class Like(models.Model):
    """
    Represents a post like mapping a user to a specific post.
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('post', 'user')

    def __str__(self):
        return f"{self.user.username} liked {self.post.title}"
    
class Bookmark(models.Model):
    """
    Represents a bookmarked post saved to the user's reading list.
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('post', 'user')

    def __str__(self):
        return f"{self.user.username} Saved {self.post.title}"
    
class History(models.Model):
    """
    Represents the reading history of a user on a post, including scroll progress.
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    scroll_progress = models.FloatField(default=0.0)
    viewed_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('post', 'user')

    def __str__(self):
        return f"{self.user.username} viewed {self.post.title}"
