from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage
from django.utils import timezone
from datetime import timedelta
from blog.models import Post, Bookmark
from blog.api_views import _check_rate_limit, _safe_page, _get_trending_post_ids


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
        'bookmarked': post.sno in bookmarked_ids if bookmarked_ids else False,
        'is_new': (timezone.now() - post.timestamp).days <= 7 if post.timestamp else False,
        'is_trending': is_trending,
    }


def api_home_posts(request):
    """Return top posts for the home page."""
    if _check_rate_limit(request, 'api_home_rate'):
        return JsonResponse({'error': 'Rate limited. Please wait 10 minutes or login to continue.'}, status=429)

    top_posts = Post.objects.filter(draft=False).defer('content').order_by('-views')[:2]

    bookmarked_ids = set()
    if request.user.is_authenticated:
        bookmarked_ids = set(Bookmark.objects.filter(user=request.user).values_list('post_id', flat=True))

    trending_post_ids = _get_trending_post_ids()
    posts_data = [_serialize_post(p, bookmarked_ids, trending_post_ids) for p in top_posts]

    return JsonResponse({
        'posts': posts_data,
    })



def api_search(request):
    """Return search results with pagination."""
    if _check_rate_limit(request, 'api_search_rate', max_requests=60, window_seconds=60):
        return JsonResponse({'error': 'Rate limited. Please wait 1 minute or login to continue.'}, status=429)

    query = request.GET.get('query', '')

    if not query:
        return JsonResponse({'posts': [], 'query': '', 'message': ''})

    if len(query) > 30:
        return JsonResponse({'posts': [], 'query': query, 'message': 'Please Enter Less Than 30 Characters'})

    from django.db.models import Q
    allPosts = Post.objects.filter(
        Q(title__icontains=query) | Q(category__icontains=query) |
        Q(content__icontains=query) | Q(author__icontains=query),
        draft=False
    ).order_by('-views')

    total_results = allPosts.count()

    # Pagination
    page = _safe_page(request)
    paginator = Paginator(allPosts, 8)
    try:
        page_obj = paginator.page(page)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    bookmarked_ids = set()
    if request.user.is_authenticated:
        bookmarked_ids = set(Bookmark.objects.filter(user=request.user).values_list('post_id', flat=True))

    trending_post_ids = _get_trending_post_ids()
    posts_data = [_serialize_post(p, bookmarked_ids, trending_post_ids) for p in page_obj]

    message = 'We searched far and wide but could not find a match. Try searching with different keywords!' if total_results == 0 else ''


    return JsonResponse({
        'posts': posts_data,
        'query': query,
        'message': message,
        'page': page_obj.number,
        'total_pages': paginator.num_pages,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'total_results': total_results,
    })
