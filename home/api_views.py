from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage
from blog.models import Post, Bookmark
from blog.api_views import _check_rate_limit, _safe_page


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
        'bookmarked': post.sno in bookmarked_ids if bookmarked_ids else False,
    }


def api_home_posts(request):
    """Return top posts for the home page."""
    if _check_rate_limit(request, 'api_home_rate'):
        return JsonResponse({'error': 'Rate limited. Please wait 10 minutes or login to continue.'}, status=429)

    top_posts = Post.objects.filter(draft=False).order_by('-views')[:2]

    bookmarked_ids = set()
    if request.user.is_authenticated:
        bookmarked_ids = set(Bookmark.objects.filter(user=request.user).values_list('post_id', flat=True))

    posts_data = [_serialize_post(p, bookmarked_ids) for p in top_posts]

    return JsonResponse({
        'posts': posts_data,
    })


def api_search(request):
    """Return search results with pagination."""
    if _check_rate_limit(request, 'api_search_rate'):
        return JsonResponse({'error': 'Rate limited. Please wait 10 minutes or login to continue.'}, status=429)

    query = request.GET.get('query', '')

    if not query:
        return JsonResponse({'posts': [], 'query': '', 'message': ''})

    if len(query) > 30:
        return JsonResponse({'posts': [], 'query': query, 'message': 'Please Enter Less Than 30 Characters'})

    allPostsTitle = Post.objects.filter(title__icontains=query, draft=False)
    allPostsCategory = Post.objects.filter(category__icontains=query, draft=False)
    allPostsContent = Post.objects.filter(content__icontains=query, draft=False)
    allPostsAuthor = Post.objects.filter(author__icontains=query, draft=False)
    allPosts = allPostsTitle.union(allPostsContent, allPostsAuthor, allPostsCategory).order_by('-views')

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

    posts_data = [_serialize_post(p, bookmarked_ids) for p in page_obj]

    message = 'No Search Result Found' if total_results == 0 else ''

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
