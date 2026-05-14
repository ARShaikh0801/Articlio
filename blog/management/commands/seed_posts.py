"""
Management command to seed dummy blog posts and comments for testing pagination.

Usage:
    python manage.py seed_posts              # Create 25 posts + 15 comments on the first post
    python manage.py seed_posts --count 50   # Create 50 posts
    python manage.py seed_posts --clear      # DELETE all dummy posts (tagged with [TEST])
"""

from django.core.management.base import BaseCommand
from blog.models import Post, BlogComment
from django.contrib.auth import get_user_model
import random

User = get_user_model()

CATEGORIES = ['Technology', 'Science', 'Health', 'Travel', 'Education', 'Finance', 'Sports', 'Entertainment']

TITLES = [
    "Understanding {cat} in the Modern World",
    "A Beginner's Guide to {cat}",
    "Top 10 Tips for {cat} Enthusiasts",
    "How {cat} Is Changing Everything",
    "The Future of {cat}: What to Expect",
    "Why {cat} Matters More Than Ever",
    "{cat} 101: Everything You Need to Know",
    "Common Mistakes in {cat} and How to Avoid Them",
    "The History of {cat} Explained Simply",
    "Breaking Down {cat} for Everyone",
    "What Nobody Tells You About {cat}",
    "{cat} Trends You Should Watch in 2026",
    "The Ultimate {cat} Resource Guide",
    "How to Get Started with {cat}",
    "Exploring the World of {cat}",
]

COMMENTS = [
    "Great article! Really enjoyed reading this.",
    "Thanks for sharing this information.",
    "Very informative and well-written.",
    "I learned something new today!",
    "Could you write more about this topic?",
    "This is exactly what I was looking for.",
    "Interesting perspective on this subject.",
    "Well researched and easy to understand.",
    "I disagree with some points but overall good read.",
    "Bookmarking this for later reference.",
    "Please keep posting content like this!",
    "This helped me understand the topic better.",
    "Excellent breakdown of a complex topic.",
    "I shared this with my friends.",
    "Looking forward to more articles from you!",
]


class Command(BaseCommand):
    help = 'Seed dummy blog posts and comments for testing pagination'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=25, help='Number of dummy posts to create (default: 25)')
        parser.add_argument('--clear', action='store_true', help='Delete all dummy [TEST] posts')

    def handle(self, *args, **options):
        if options['clear']:
            # Delete dummy test posts
            post_count, _ = Post.objects.filter(title__startswith='[TEST]').delete()
            # Delete dummy test users
            user_count, _ = User.objects.filter(username__startswith='dummy_test_user_').delete()
            
            self.stdout.write(self.style.SUCCESS(f'✅ Deleted {post_count} dummy posts and {user_count} dummy users.'))
            return

        # Find an author user, or use a placeholder name
        author_user = User.objects.filter(role='author', verified=True).first()
        author_name = author_user.name if author_user else 'Test Author'

        count = options['count']
        created = 0

        for i in range(count):
            cat = random.choice(CATEGORIES)
            title_template = TITLES[i % len(TITLES)]
            title = f"[TEST] {title_template.format(cat=cat)}"
            slug = f"test-post-{i+1}-{cat.lower()}-{random.randint(1000,9999)}"

            content = f"<p>This is a dummy test post about <strong>{cat}</strong>. " \
                      f"It was auto-generated for testing pagination. " \
                      f"Lorem ipsum dolor sit amet, consectetur adipiscing elit. " \
                      f"Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>" \
                      f"<p>Post number <strong>{i+1}</strong> of {count}.</p>"

            summary = f"A test post about {cat} — auto-generated for pagination testing. Post {i+1} of {count}."

            Post.objects.create(
                title=title,
                content=content,
                summary=summary,
                author=author_name,
                slug=slug,
                category=cat,
                views=random.randint(0, 500),
                likes=random.randint(0, 50),
                draft=False,
            )
            created += 1

        self.stdout.write(self.style.SUCCESS(f'✅ Created {created} dummy posts.'))

        # Also create some comments on the first test post for testing comment pagination
        first_test_post = Post.objects.filter(title__startswith='[TEST]').first()
        if first_test_post:
            comment_count = min(15, len(COMMENTS))
            for j in range(comment_count):
                # Create a dummy user for each comment so they aren't "own comments"
                dummy_username = f'dummy_test_user_{j}_{random.randint(1000, 9999)}'
                dummy_user = User.objects.create_user(
                    username=dummy_username,
                    password='password123',
                    name=f'Test User {j+1}'
                )
                
                BlogComment.objects.create(
                    comment=f"[TEST] {COMMENTS[j]}",
                    user=dummy_user,
                    post=first_test_post,
                    parent=None,
                )
            self.stdout.write(self.style.SUCCESS(
                f'✅ Created {comment_count} dummy comments on post: "{first_test_post.title}"'
            ))

        self.stdout.write(self.style.WARNING(
            f'\n💡 To clean up later, run: python manage.py seed_posts --clear'
        ))
