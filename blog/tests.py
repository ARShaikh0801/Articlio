from django.test import TestCase
from django.urls import reverse
from blog.models import Post

class RSSFeedTest(TestCase):
    def setUp(self):
        # Create a test post
        self.post = Post.objects.create(
            title="Test Post Title",
            content="<p>Test content for the blog post.</p>",
            summary="Test Summary",
            author="TestAuthor",
            slug="test-post-slug",
            draft=False
        )

    def test_rss_feed_status_code(self):
        response = self.client.get(reverse('blog_feed'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/rss+xml; charset=utf-8')

    def test_rss_feed_content(self):
        response = self.client.get(reverse('blog_feed'))
        content = response.content.decode('utf-8')
        self.assertIn("Test Post Title", content)
        self.assertIn("Test Summary", content)
        self.assertIn("/blog/test-post-slug", content)
