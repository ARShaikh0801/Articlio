from home.models import CustomUser, Visitor

def footer_stats(request):
    """
    Context processor to return statistics for the footer.
    1st: Number of authors
    2nd: Number of users (authors + readers)
    3rd: Total visitors
    """
    try:
        author_count = CustomUser.objects.filter(role='author').count()
        total_users_count = CustomUser.objects.count()
        total_visitors_count = Visitor.objects.count()
    except Exception:
        author_count = 0
        total_users_count = 0
        total_visitors_count = 0

    return {
        'footer_author_count': author_count,
        'footer_total_users_count': total_users_count,
        'footer_total_visitors_count': total_visitors_count,
    }
