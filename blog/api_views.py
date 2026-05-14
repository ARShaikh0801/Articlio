from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Post, BlogComment, Like, Bookmark
import time


def _safe_page(request, default=1):
    """Safely parse the 'page' query param, clamping to >= 1."""
    try:
        page = int(request.GET.get('page', default))
        return max(1, page)
    except (TypeError, ValueError):
        return 1


def _check_rate_limit(request, key='api_requests', max_requests=15, window_seconds=600):
    """Simple session-based rate limiter. Returns True if rate-limited."""
    # Unauthenticated users only
    if request.user.is_authenticated:
        return False
        
    now = time.time()
    timestamps = request.session.get(key, [])
    # Prune old timestamps outside the window
    timestamps = [t for t in timestamps if now - t < window_seconds]
    if len(timestamps) >= max_requests:
        return True
    timestamps.append(now)
    request.session[key] = timestamps
    request.session.modified = True
    return False


def _serialize_post(post, bookmarked_ids=None):
    """Serialize a Post object to a dict for JSON response."""
    return {
        'sno': post.sno,
        'title': post.title,
        'summary': post.summary,
        'author': post.author,
        'slug': post.slug,
        'category': post.category,
        'views': post.views,
        'likes': post.likes,
        'timestamp': post.timestamp.strftime('%b. %d, %Y, %I:%M %p').replace(' 0', ' ') if post.timestamp else '',
        'updated_at': post.updated_at.strftime('%b. %d, %Y, %I:%M %p').replace(' 0', ' ') if post.updated_at else '',
        'bookmarked': post.sno in bookmarked_ids if bookmarked_ids else False,
    }


def _serialize_comment(comment, replies_dict, current_user=None):
    """Serialize a comment with its replies."""
    from django.contrib.humanize.templatetags.humanize import naturaltime
    replies = replies_dict.get(comment.sno, [])
    return {
        'sno': comment.sno,
        'comment': comment.comment,
        'username': comment.user.username,
        'is_own': current_user == comment.user if current_user else False,
        'timestamp': naturaltime(comment.timestamp),
        'replies': [
            {
                'sno': r.sno,
                'comment': r.comment,
                'username': r.user.username,
                'timestamp': naturaltime(r.timestamp),
            }
            for r in replies
        ],
    }


def api_posts(request):
    """Return published posts with filter/sort support and pagination."""
    if _check_rate_limit(request, 'api_posts_rate'):
        return JsonResponse({'error': 'Too many requests. Please wait 10 minutes or login to continue.'}, status=429)

    allPosts = Post.objects.filter(draft=False)

    # Get filter params
    filtered = request.GET.get('filter', 'all')
    authors_filter = request.GET.get('authors', 'all')
    category_filter = request.GET.get('category', 'all')

    # Apply sorting
    if filtered == 'liked':
        allPosts = allPosts.order_by('-likes')
    elif filtered == 'unliked':
        allPosts = allPosts.order_by('likes')
    elif filtered == 'viewed':
        allPosts = allPosts.order_by('-views')
    elif filtered == 'unviewed':
        allPosts = allPosts.order_by('views')
    elif filtered == 'latest':
        allPosts = allPosts.order_by('-timestamp')
    elif filtered == 'old':
        allPosts = allPosts.order_by('timestamp')
    else:
        # Default ordering to prevent UnorderedObjectListWarning during pagination
        allPosts = allPosts.order_by('-timestamp')

    # Apply author/category filters
    if authors_filter != 'all':
        allPosts = allPosts.filter(author=authors_filter)
    if category_filter != 'all':
        allPosts = allPosts.filter(category=category_filter)

    # Get unique authors and categories
    authors = list(Post.objects.filter(draft=False).values_list('author', flat=True).distinct())
    categories = list(Post.objects.filter(draft=False).values_list('category', flat=True).distinct())

    # Pagination
    page = _safe_page(request)
    paginator = Paginator(allPosts, 8)
    try:
        page_obj = paginator.page(page)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # Get bookmarked IDs
    bookmarked_ids = set()
    if request.user.is_authenticated:
        bookmarked_ids = set(Bookmark.objects.filter(user=request.user).values_list('post_id', flat=True))

    posts_data = [_serialize_post(p, bookmarked_ids) for p in page_obj]

    return JsonResponse({
        'posts': posts_data,
        'authors': authors,
        'categories': categories,
        'filter': filtered,
        'selectedAuthor': authors_filter,
        'selectedCategory': category_filter,
        'page': page_obj.number,
        'total_pages': paginator.num_pages,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'total_posts': paginator.count,
    })


def api_post_state(request, slug):
    """Return like/bookmark state and related posts for a blog post."""
    if _check_rate_limit(request, 'api_post_view_rate', max_requests=5, window_seconds=1800):
        return JsonResponse({'error': 'Rate limit exceeded. Please wait 30 minutes or login to continue.'}, status=429)

    post = get_object_or_404(Post, slug=slug, draft=False)

    liked = False
    bookmarked = False
    if request.user.is_authenticated:
        liked = Like.objects.filter(post=post, user=request.user).exists()
        bookmarked = Bookmark.objects.filter(post=post, user=request.user).exists()

    # Related posts
    interested = Post.objects.filter(draft=False, category=post.category).exclude(sno=post.sno)[:4]
    interested_data = [
        {
            'title': p.title,
            'slug': p.slug,
            'category': p.category,
            'summary': p.summary[:100] + '…' if len(p.summary) > 100 else p.summary,
        }
        for p in interested
    ]

    return JsonResponse({
        'liked': liked,
        'bookmarked': bookmarked,
        'likes': post.likes,
        'views': post.views,
        'interestedPosts': interested_data,
    })


def api_comments(request, slug):
    """Return the comment tree for a blog post with pagination."""
    if _check_rate_limit(request, 'api_comments_view_rate', max_requests=5, window_seconds=1800):
        return JsonResponse({'error': 'Rate limit exceeded. Please wait 30 minutes or login to continue.'}, status=429)

    post = get_object_or_404(Post, slug=slug, draft=False)

    all_top_level = BlogComment.objects.filter(post=post, parent=None).order_by('-timestamp')
    replies = BlogComment.objects.filter(post=post).exclude(parent=None)

    replies_dict = {}
    for reply in replies:
        if reply.parent.sno not in replies_dict:
            replies_dict[reply.parent.sno] = [reply]
        else:
            replies_dict[reply.parent.sno].append(reply)

    current_user = request.user if request.user.is_authenticated else None
    total_count = all_top_level.count()

    # Separate own comments (always fully returned) and others (paginated)
    own_comments = []
    other_top_level = []
    for c in all_top_level:
        if current_user and c.user == current_user:
            own_comments.append(_serialize_comment(c, replies_dict, current_user))
        else:
            other_top_level.append(c)

    # Paginate the 'other' comments
    page = _safe_page(request)
    paginator = Paginator(other_top_level, 5)
    try:
        page_obj = paginator.page(page)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages) if paginator.num_pages > 0 else paginator.page(1)

    other_comments = [_serialize_comment(c, replies_dict, current_user) for c in page_obj]

    return JsonResponse({
        'own_comments': own_comments,
        'other_comments': other_comments,
        'total': total_count,
        'post_sno': post.sno,
        'page': page_obj.number if paginator.num_pages > 0 else 1,
        'total_pages': paginator.num_pages,
        'has_next': page_obj.has_next() if paginator.num_pages > 0 else False,
    })


def api_bookmarks(request):
    """Return user's bookmarked posts with pagination."""
    if not request.user.is_authenticated:
        return JsonResponse({'posts': [], 'authenticated': False})

    saved_posts = Post.objects.filter(bookmark__user=request.user).distinct().order_by('-bookmark__id')

    # Pagination
    page = _safe_page(request)
    paginator = Paginator(saved_posts, 8)
    try:
        page_obj = paginator.page(page)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    bookmarked_ids = set(Bookmark.objects.filter(user=request.user).values_list('post_id', flat=True))
    posts_data = [_serialize_post(p, bookmarked_ids) for p in page_obj]

    return JsonResponse({
        'posts': posts_data,
        'authenticated': True,
        'page': page_obj.number,
        'total_pages': paginator.num_pages,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'total_posts': paginator.count,
    })


def api_my_blogs(request):
    """Return user's draft and published blogs with per-tab pagination."""
    if not request.user.is_authenticated:
        return JsonResponse({'blogs': [], 'authenticated': False})

    if request.user.role != 'author' or not request.user.verified:
        return JsonResponse({'blogs': [], 'authenticated': True, 'authorized': False})

    tab = request.GET.get('tab', 'drafts')
    if tab not in ('drafts', 'published'):
        tab = 'drafts'

    drafts_qs = Post.objects.filter(author=request.user.name, draft=True)
    published_qs = Post.objects.filter(author=request.user.name, draft=False)
    total_drafts = drafts_qs.count()
    total_published = published_qs.count()
    has_drafts = total_drafts > 0

    if tab == 'drafts':
        queryset = drafts_qs.order_by('-updated_at')
    else:
        queryset = published_qs.order_by('-updated_at')

    page = _safe_page(request)
    paginator = Paginator(queryset, 6)
    try:
        page_obj = paginator.page(page)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages) if paginator.num_pages > 0 else paginator.page(1)

    def serialize_blog(b):
        data = {
            'title': b.title,
            'slug': b.slug,
            'category': b.category,
            'summary': b.summary,
            'timestamp': b.timestamp.strftime('%b. %d, %Y, %I:%M %p').replace(' 0', ' ') if b.timestamp else '',
            'updated_at': b.updated_at.strftime('%b. %d, %Y, %I:%M %p').replace(' 0', ' ') if b.updated_at else '',
        }
        if not b.draft:
            data['views'] = b.views
            data['likes'] = b.likes
        return data

    blogs_data = [serialize_blog(b) for b in page_obj]

    return JsonResponse({
        'blogs': blogs_data,
        'tab': tab,
        'authenticated': True,
        'authorized': True,
        'has_drafts': has_drafts,
        'total_drafts': total_drafts,
        'total_published': total_published,
        'page': page_obj.number if paginator.num_pages > 0 else 1,
        'total_pages': paginator.num_pages,
        'has_next': page_obj.has_next() if paginator.num_pages > 0 else False,
        'has_previous': page_obj.has_previous() if paginator.num_pages > 0 else False,
    })
