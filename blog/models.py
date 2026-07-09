import re
from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()
from django.utils.timezone import now
from django.utils.html import strip_tags

class Post(models.Model):
    """
    Represents a blog post. Tracks metadata such as views, likes, category, 
    and draft status.
    """
    sno=models.AutoField(primary_key=True)
    title=models.CharField(max_length=200)
    content=models.TextField()
    summary = models.TextField(max_length=200, blank=True)
    author=models.CharField(max_length=100, db_index=True)
    slug=models.CharField(max_length=100,unique=True)
    category=models.CharField(max_length=200, default="general", db_index=True)
    views=models.IntegerField(default=0,editable=False, db_index=True)
    timestamp=models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes=models.IntegerField(default=0,editable=False)
    draft=models.BooleanField(default=False, db_index=True)
    reading_time_minutes = models.PositiveIntegerField(default=1, editable=False)

    class Meta:
        indexes = [
            models.Index(fields=['draft', 'category'], name='idx_post_draft_category'),
            models.Index(fields=['draft', '-views'], name='idx_post_draft_views'),
            models.Index(fields=['draft', '-timestamp'], name='idx_post_draft_timestamp'),
        ]

    def _compute_reading_time(self):
        """Compute estimated reading time in minutes (based on ~200 words per minute)."""
        text = strip_tags(self.content or '')
        text = re.sub(r'\s+', ' ', text).strip()
        word_count = len(text.split())
        return max(1, round(word_count / 200))

    @property
    def reading_time(self):
        """Return stored reading time, falling back to computation if needed."""
        if self.reading_time_minutes:
            return self.reading_time_minutes
        return self._compute_reading_time()

    def save(self, *args, **kwargs):
        # Auto-compute reading_time on every save (unless only updating specific fields
        # that don't include content)
        update_fields = kwargs.get('update_fields')
        if update_fields is None or 'content' in update_fields:
            self.reading_time_minutes = self._compute_reading_time()
            if update_fields and 'reading_time_minutes' not in update_fields:
                kwargs['update_fields'] = list(update_fields) + ['reading_time_minutes']
        super().save(*args, **kwargs)

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
    likes=models.ManyToManyField(User,related_name='comment_likes',blank=True)

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
        indexes = [
            models.Index(fields=['user', '-viewed_at'], name='idx_history_user_viewed'),
        ]

    def __str__(self):
        return f"{self.user.username} viewed {self.post.title}"

class Highlight(models.Model):
    """
    Represents a user's text highlight & annotation on a blog post.
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_offset = models.IntegerField()
    end_offset = models.IntegerField()
    text = models.TextField()
    note = models.TextField(blank=True, null=True)
    color = models.CharField(max_length=20, default='yellow')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['post', 'user'], name='idx_highlight_post_user'),
        ]

    def __str__(self):
        return f"{self.user.username}'s highlight on {self.post.title}"


class Reaction(models.Model):
    """
    Represents user reactions to a post. Allowed multiple times per reaction type.
    """
    REACTION_TYPES = [
        ('fire', 'Fire'),
        ('insightful', 'Insightful'),
        ('celebrate', 'Celebrate'),
        ('surprised', 'Surprised'),
    ]
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reactions')
    type = models.CharField(max_length=20, choices=REACTION_TYPES)
    count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('post', 'user', 'type')
        indexes = [
            models.Index(fields=['post', 'type'], name='idx_reaction_post_type'),
        ]

    def __str__(self):
        return f"{self.user.username} reacted {self.type} x{self.count} on {self.post.title}"


