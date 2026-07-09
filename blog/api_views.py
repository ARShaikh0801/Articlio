from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from datetime import timedelta
from .models import Post, BlogComment, Like, Bookmark, History, Highlight, Reaction
from django.db.models import Count, Sum, Subquery, OuterRef, Max
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


def _get_trending_post_ids():
    """Return the set of post sno IDs representing the top 1 viewed post in each category.
    Uses a single subquery instead of per-category loops."""
    # Subquery: for each category, find the max views among non-draft posts
    max_views_subquery = Post.objects.filter(
        draft=False, category=OuterRef('category')
    ).order_by('-views').values('views')[:1]

    # Find posts whose views equal the max in their category
    trending_posts = Post.objects.filter(
        draft=False,
        views=Subquery(max_views_subquery)
    ).values_list('sno', flat=True)

    return set(trending_posts)


def _serialize_post(post, bookmarked_ids=None, trending_post_ids=None):
    """Serialize a Post object to a dict for JSON response."""
    is_trending = False
    if trending_post_ids is not None:
        is_trending = post.sno in trending_post_ids
    return {
        'sno': post.sno,
        'title': post.title,
        'summary': post.summary,
        'author': post.author,
        'slug': post.slug,
        'category': post.category,
        'views': post.views,
        'likes': post.likes,
        'reading_time': post.reading_time,
        'timestamp': post.timestamp.strftime('%b. %d, %Y, %I:%M %p').replace(' 0', ' ') if post.timestamp else '',
        'updated_at': post.updated_at.strftime('%b. %d, %Y, %I:%M %p').replace(' 0', ' ') if post.updated_at else '',
        'bookmarked': post.sno in bookmarked_ids if bookmarked_ids else False,
        'is_new': (timezone.now() - post.timestamp).days <= 7 if post.timestamp else False,
        'is_trending': is_trending,
    }



def _serialize_comment(comment, replies_dict, current_user=None, liked_comment_ids=None):
    """Serialize a comment with its replies."""
    from django.contrib.humanize.templatetags.humanize import naturaltime
    replies = replies_dict.get(comment.sno, [])
    if liked_comment_ids is None:
        liked_comment_ids = set()
    
    # Put user's own replies on top, keeping others ordered by like count
    own_replies = []
    other_replies = []
    for r in replies:
        if current_user and r.user == current_user:
            own_replies.append(r)
        else:
            other_replies.append(r)
    sorted_replies = own_replies + other_replies

    return {
        'sno': comment.sno,
        'comment': comment.comment,
        'username': comment.user.username,
        'is_own': current_user == comment.user if current_user else False,
        'timestamp': naturaltime(comment.timestamp),
        'likes_count': getattr(comment, 'num_likes', 0),
        'liked': comment.sno in liked_comment_ids,
        'replies': [
            {
                'sno': r.sno,
                'comment': r.comment,
                'username': r.user.username,
                'timestamp': naturaltime(r.timestamp),
                'likes_count': getattr(r, 'num_likes', 0),
                'liked': r.sno in liked_comment_ids,
                'is_own': current_user == r.user if current_user else False,
            }
            for r in sorted_replies
        ],
    }


def api_posts(request):
    """Return published posts with filter/sort support and pagination."""
    if not request.user.is_authenticated and _check_rate_limit(request, 'api_posts_rate'):
        return JsonResponse({'error': 'Too many requests. Please wait 10 minutes or login to continue.'}, status=429)

    allPosts = Post.objects.filter(draft=False).defer('content')

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

    # Get unique authors and categories in a single query
    author_category_pairs = Post.objects.filter(draft=False).values_list('author', 'category')
    authors = sorted(set(pair[0] for pair in author_category_pairs))
    categories = sorted(set(pair[1] for pair in author_category_pairs))

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

    trending_post_ids = _get_trending_post_ids()
    posts_data = [_serialize_post(p, bookmarked_ids, trending_post_ids) for p in page_obj]

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
    scroll_progress = 0.0
    if request.user.is_authenticated:
        liked = Like.objects.filter(post=post, user=request.user).exists()
        bookmarked = Bookmark.objects.filter(post=post, user=request.user).exists()
        history_entry = History.objects.filter(post=post, user=request.user).first()
        if history_entry:
            scroll_progress = history_entry.scroll_progress

    # Related posts: Prioritize same category by popularity, fallback to overall popularity
    interested = list(Post.objects.filter(draft=False, category=post.category).exclude(sno=post.sno).defer('content').order_by('-views', '-likes')[:4])
    if len(interested) < 4:
        exclude_snos = [p.sno for p in interested] + [post.sno]
        fallback_posts = Post.objects.filter(draft=False).exclude(sno__in=exclude_snos).defer('content').order_by('-views', '-likes')[:4 - len(interested)]
        interested.extend(fallback_posts)

    interested_data = [
        {
            'title': p.title,
            'slug': p.slug,
            'category': p.category,
            'summary': p.summary[:100] + '…' if len(p.summary) > 100 else p.summary,
            'likes': p.likes,
            'views': p.views,
            'reading_time': p.reading_time,
            'timestamp': p.timestamp.strftime('%b. %d, %Y').replace(' 0', ' ') if p.timestamp else '',
        }
        for p in interested
    ]

    # Bulk-fetch reaction totals and user counts in 2 queries instead of 8
    valid_types = ['fire', 'insightful', 'celebrate', 'surprised']
    reactions = {r_type: 0 for r_type in valid_types}
    user_reactions = {r_type: 0 for r_type in valid_types}

    totals_qs = Reaction.objects.filter(post=post, type__in=valid_types).values('type').annotate(total=Sum('count'))
    for row in totals_qs:
        reactions[row['type']] = row['total'] or 0

    if request.user.is_authenticated:
        user_qs = Reaction.objects.filter(post=post, user=request.user, type__in=valid_types).values('type', 'count')
        for row in user_qs:
            user_reactions[row['type']] = row['count'] or 0

    return JsonResponse({
        'liked': liked,
        'bookmarked': bookmarked,
        'likes': post.likes,
        'views': post.views,
        'reading_time': post.reading_time,
        'scroll_progress': scroll_progress,
        'interestedPosts': interested_data,
        'reactions': reactions,
        'user_reactions': user_reactions,
    })


def api_comments(request, slug):
    """Return the comment tree for a blog post with pagination."""
    if not request.user.is_authenticated and _check_rate_limit(request, 'api_comments_view_rate', max_requests=60, window_seconds=60):
        return JsonResponse({'error': 'Rate limit exceeded. Please wait 30 minutes or login to continue.'}, status=429)

    post = get_object_or_404(Post, slug=slug, draft=False)

    all_top_level = BlogComment.objects.filter(post=post, parent=None).select_related('user').annotate(num_likes=Count('likes')).order_by('-num_likes', '-timestamp')
    replies = BlogComment.objects.filter(post=post).exclude(parent=None).select_related('user').annotate(num_likes=Count('likes')).order_by('-num_likes', '-timestamp')

    replies_dict = {}
    for reply in replies:
        if reply.parent.sno not in replies_dict:
            replies_dict[reply.parent.sno] = [reply]
        else:
            replies_dict[reply.parent.sno].append(reply)

    current_user = request.user if request.user.is_authenticated else None
    total_count = all_top_level.count()

    liked_comment_ids = set()
    if current_user:
        liked_comment_ids = set(current_user.comment_likes.filter(post=post).values_list('sno', flat=True))

    # Separate own comments (always fully returned) and others (paginated)
    own_comments = []
    other_top_level = []
    for c in all_top_level:
        if current_user and c.user == current_user:
            own_comments.append(_serialize_comment(c, replies_dict, current_user, liked_comment_ids))
        else:
            other_top_level.append(c)

    # Paginate the 'other' comments
    page = _safe_page(request)
    paginator = Paginator(other_top_level, 5)
    try:
        page_obj = paginator.page(page)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages) if paginator.num_pages > 0 else paginator.page(1)

    other_comments = [_serialize_comment(c, replies_dict, current_user, liked_comment_ids) for c in page_obj]

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

    saved_posts = Post.objects.filter(bookmark__user=request.user).defer('content').distinct().order_by('-bookmark__id')

    # Pagination
    page = _safe_page(request)
    paginator = Paginator(saved_posts, 8)
    try:
        page_obj = paginator.page(page)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    bookmarked_ids = set(Bookmark.objects.filter(user=request.user).values_list('post_id', flat=True))
    trending_post_ids = _get_trending_post_ids()
    posts_data = [_serialize_post(p, bookmarked_ids, trending_post_ids) for p in page_obj]

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

    query = request.GET.get('query', '').strip()

    drafts_qs = Post.objects.filter(author=request.user.name, draft=True).defer('content')
    published_qs = Post.objects.filter(author=request.user.name, draft=False).defer('content')
    
    if query:
        from django.db.models import Q
        search_filter = Q(title__icontains=query) | Q(content__icontains=query) | Q(category__icontains=query)
        drafts_qs = drafts_qs.filter(search_filter)
        published_qs = published_qs.filter(search_filter)

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
            data['reading_time'] = b.reading_time
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


def api_track_history(request):
    """Save or update a history entry (scroll progress + viewed_at) for authenticated users."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({'status': 'ok', 'stored': 'client'})

    import json
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    post_sno = data.get('post_sno')
    scroll_progress = data.get('scroll_progress', 0.0)

    # Handle clear all history
    if data.get('clear_all'):
        History.objects.filter(user=request.user).delete()
        return JsonResponse({'status': 'ok', 'cleared': True})

    # Handle remove single entry
    remove_sno = data.get('remove_sno')
    if remove_sno:
        History.objects.filter(user=request.user, post__sno=remove_sno).delete()
        return JsonResponse({'status': 'ok', 'removed': True})

    if not post_sno:
        return JsonResponse({'error': 'post_sno required'}, status=400)

    try:
        post = Post.objects.get(sno=post_sno, draft=False)
    except Post.DoesNotExist:
        return JsonResponse({'error': 'Post not found'}, status=404)

    try:
        scroll_progress = float(scroll_progress)
    except (TypeError, ValueError):
        scroll_progress = 0.0

    History.objects.update_or_create(
        post=post,
        user=request.user,
        defaults={'scroll_progress': scroll_progress},
    )

    # Cleanup: delete entries older than 90 days for this user
    from django.utils import timezone
    import datetime
    cutoff = timezone.now() - datetime.timedelta(days=90)
    History.objects.filter(user=request.user, viewed_at__lt=cutoff).delete()

    return JsonResponse({'status': 'ok', 'stored': 'server'})


def api_history(request):
    """Return history posts.
    Authenticated: paginated from DB.
    Unauthenticated: POST with list of SNOs from localStorage.
    """
    if request.user.is_authenticated:
        # GET: paginated history from DB
        from django.utils import timezone
        import datetime
        cutoff = timezone.now() - datetime.timedelta(days=90)

        # Cleanup old entries
        History.objects.filter(user=request.user, viewed_at__lt=cutoff).delete()

        history_qs = History.objects.filter(
            user=request.user,
            viewed_at__gte=cutoff,
        ).select_related('post').defer('post__content')

        # Apply sorting
        sort_param = request.GET.get('sort', 'recent')
        now = timezone.now()
        if sort_param == 'oldest':
            history_qs = history_qs.order_by('viewed_at')
        elif sort_param == 'progress-high':
            history_qs = history_qs.order_by('-scroll_progress')
        elif sort_param == 'progress-low':
            history_qs = history_qs.order_by('scroll_progress')
        elif sort_param == 'unfinished':
            history_qs = history_qs.filter(scroll_progress__lt=100).order_by('-viewed_at')
        elif sort_param == '1-month-older':
            one_month_ago = now - datetime.timedelta(days=30)
            history_qs = history_qs.filter(viewed_at__lt=one_month_ago).order_by('-viewed_at')
        elif sort_param == '2-months-older':
            two_months_ago = now - datetime.timedelta(days=60)
            history_qs = history_qs.filter(viewed_at__lt=two_months_ago).order_by('-viewed_at')
        else:  # 'recent'
            history_qs = history_qs.order_by('-viewed_at')

        page = _safe_page(request)
        paginator = Paginator(history_qs, 8)
        try:
            page_obj = paginator.page(page)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages) if paginator.num_pages > 0 else paginator.page(1)

        bookmarked_ids = set(Bookmark.objects.filter(user=request.user).values_list('post_id', flat=True))
        trending_post_ids = _get_trending_post_ids()

        posts_data = []
        for h in page_obj:
            p = h.post
            if p.draft:
                continue
            d = _serialize_post(p, bookmarked_ids, trending_post_ids)
            d['scroll_progress'] = h.scroll_progress
            d['viewed_at'] = h.viewed_at.strftime('%b. %d, %Y, %I:%M %p').replace(' 0', ' ') if h.viewed_at else ''
            posts_data.append(d)

        return JsonResponse({
            'posts': posts_data,
            'authenticated': True,
            'page': page_obj.number if paginator.num_pages > 0 else 1,
            'total_pages': paginator.num_pages,
            'has_next': page_obj.has_next() if paginator.num_pages > 0 else False,
            'has_previous': page_obj.has_previous() if paginator.num_pages > 0 else False,
            'total_posts': paginator.count,
        })
    else:
        # Unauthenticated: accept POST with list of SNOs
        if request.method != 'POST':
            return JsonResponse({'posts': [], 'authenticated': False})

        import json
        try:
            data = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        sno_list = data.get('snos', [])
        if not isinstance(sno_list, list):
            return JsonResponse({'posts': [], 'authenticated': False})

        # Only take first 50 to prevent abuse
        sno_list = sno_list[:50]
        posts = Post.objects.filter(sno__in=sno_list, draft=False).defer('content')

        # Maintain the order from the client (most recent first)
        post_map = {p.sno: p for p in posts}
        posts_data = []
        for sno in sno_list:
            if sno in post_map:
                posts_data.append(_serialize_post(post_map[sno]))

        return JsonResponse({
            'posts': posts_data,
            'authenticated': False,
        })


def api_highlights(request, slug):
    """Return all highlights for a blog post."""
    post = get_object_or_404(Post, slug=slug, draft=False)
    
    if request.user.is_authenticated:
        highlights = Highlight.objects.filter(post=post, user=request.user).order_by('start_offset')
        data = [{
            'id': h.id,
            'start': h.start_offset,
            'end': h.end_offset,
            'text': h.text,
            'note': h.note or '',
            'color': h.color
        } for h in highlights]
        return JsonResponse({'highlights': data, 'authenticated': True})
    else:
        return JsonResponse({'highlights': [], 'authenticated': False})


def api_create_highlight(request):
    """Create a new highlight for a blog post (authenticated only)."""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
        
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
        
    import json
    try:
        data = json.loads(request.body)
        post_sno = data.get('post_sno')
        start = int(data.get('start'))
        end = int(data.get('end'))
        text = data.get('text', '')
        note = data.get('note', '')
        color = data.get('color', 'yellow')
    except (json.JSONDecodeError, ValueError, TypeError) as e:
        return JsonResponse({'error': 'Invalid request data'}, status=400)
        
    post = get_object_or_404(Post, sno=post_sno)
    
    # Avoid duplicate highlights at the exact same location
    existing = Highlight.objects.filter(post=post, user=request.user, start_offset=start, end_offset=end).first()
    if existing:
        existing.text = text
        existing.note = note
        existing.color = color
        existing.save()
        h = existing
    else:
        h = Highlight.objects.create(
            post=post,
            user=request.user,
            start_offset=start,
            end_offset=end,
            text=text,
            note=note,
            color=color
        )
        
    return JsonResponse({
        'status': 'success',
        'highlight': {
            'id': h.id,
            'start': h.start_offset,
            'end': h.end_offset,
            'text': h.text,
            'note': h.note or '',
            'color': h.color
        }
    })


def api_update_highlight(request, id):
    """Update highlight note/color (authenticated only)."""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
        
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
        
    h = get_object_or_404(Highlight, id=id, user=request.user)
    
    import json
    try:
        data = json.loads(request.body)
        h.note = data.get('note', h.note)
        h.color = data.get('color', h.color)
        h.save()
    except (json.JSONDecodeError, ValueError) as e:
        return JsonResponse({'error': 'Invalid request data'}, status=400)
        
    return JsonResponse({
        'status': 'success',
        'highlight': {
            'id': h.id,
            'start': h.start_offset,
            'end': h.end_offset,
            'text': h.text,
            'note': h.note or '',
            'color': h.color
        }
    })


def api_delete_highlight(request, id):
    """Delete a highlight (authenticated only)."""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
        
    if request.method not in ['POST', 'DELETE']:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
        
    h = get_object_or_404(Highlight, id=id, user=request.user)
    h.delete()
    
    return JsonResponse({'status': 'success'})

