from django.contrib import admin
from .models import Post,BlogComment


@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin):
    list_display = ('comment', 'user', 'post', 'timestamp')
    readonly_fields=('user','post','timestamp','comment','parent')

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'author', 'updated_at', 'category')
    list_filter = ('category', 'timestamp', 'updated_at', 'author','draft')
    readonly_fields=('slug','title','views','likes','timestamp','updated_at','content','author','category','draft')
    search_fields = ('title', 'content','author','category','slug')
    ordering = ['views', 'timestamp','updated_at','likes']