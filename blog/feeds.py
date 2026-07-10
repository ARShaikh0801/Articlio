from django.contrib.syndication.views import Feed
from django.utils.html import strip_tags
from .models import Post

class LatestPostsFeed(Feed):
    title = "Articlio Blog Feed"
    link = "/"
    description = "Thoughtful articles, insights, and tutorials on Articlio Blog."

    def items(self):
        # Only non-draft posts, ordered by latest publication time, limit to 20
        return Post.objects.filter(draft=False).order_by('-timestamp')[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        if item.summary:
            return item.summary
        # Fallback to post content snippet
        clean_content = strip_tags(item.content or '')
        if len(clean_content) > 200:
            return clean_content[:200] + '...'
        return clean_content

    def item_pubdate(self, item):
        return item.timestamp

    def item_author_name(self, item):
        return item.author
