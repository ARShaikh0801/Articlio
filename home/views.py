from django.shortcuts import render,redirect,get_object_or_404
from django.http import JsonResponse
import json
from django.contrib import messages
from home.models import Contact
from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib.auth import authenticate,login,logout
from django.urls import reverse
import random
import time
from home.utils import send_verification_email

def home(request):
    """
    Renders the homepage for Articlio.
    """
    return render(request,'home/home.html')

def contact(request):
    """
    Handles user queries and message submissions via the Contact page contact form.
    """
    if request.user.is_authenticated:
        prevMsgs=Contact.objects.filter(email=request.user.email)
        if request.method=='POST':
            name=request.POST['name']
            email=request.POST['email']
            phone=request.POST['phone']
            content=request.POST['content']
            if len(name)<2 or len(email)<3 or len(phone)<10 or len(content)<4:
                messages.error(request,"Please fill the form correctly...")
            else:
                contact=Contact(name=name,email=email,phone=phone,content=content)
                contact.save()
                messages.success(request,'Thanks for contacting us...')
                prevMsgs=Contact.objects.filter(email=email)
    else:
        prevMsgs=Contact.objects.none()
        messages.warning(request,"Please Login To Contact Us...")
    return render(request,'home/contact.html',{'prevMsgs':prevMsgs})

def about(request):
    """
    Renders the About page describing the platform.
    """
    return render(request,'home/about.html')

def search(request):
    """
    Redirects blank searches and handles query input parameters to render the search page.
    """
    query=request.GET.get('query')
    if query=='':
        return redirect('blogHome')
    context={'query':query}
    return render(request,'home/search.html',context)

def handleSignup(request):
    if request.method=='POST':
        username=request.POST['username']
        name=request.POST['name']
        email=request.POST['email']
        role=request.POST['role']
        pass1=request.POST['pass1']
        pass2=request.POST['pass2']
        verifiedstr=request.POST['verified']
        terms=request.POST.get('terms','')
        privacy=request.POST.get('privacy','')
        
        context = {
            'username': username,
            'name': name,
            'email': email,
            'role': role,
            'terms': terms,
            'privacy': privacy
        }
        
        if not (username and name and email and role and pass1 and pass2 and verifiedstr):
            messages.error(request,"All Fields Are Compulsory")
            return render(request,'home/signup.html', context)
        if verifiedstr=='False':
            verified=False
        else:
            verified=True
        if len(username)>10:
            messages.error(request,"Username Must Be Less Than 10 Character")
            return render(request,'home/signup.html', context)
        if not username.isalnum():
            messages.error(request,"Username Should Contain Letters And Numbers Only")
            return render(request,'home/signup.html', context)
        if len(pass1)<6:
            messages.error(request,"Password Should Be At Least 6 Characters Long")
            return render(request,'home/signup.html', context)
        if pass1!=pass2:
            messages.error(request,"Password Do Not Match")
            return render(request,'home/signup.html', context)
        if User.objects.filter(username=username,email=email).exists():
            messages.error(request,"Account Already Exists Please Login")
            return render(request,'home/signup.html', context)
        if User.objects.filter(username=username).exists():
            messages.error(request,"Username Already Exists")
            return render(request,'home/signup.html', context)
        if User.objects.filter(email=email).exists():
            messages.error(request,"Email Already Exists")
            return render(request,'home/signup.html', context)
        if not terms:
            messages.error(request,"Please Accept Terms And Conditions")
            return render(request,'home/signup.html', context)
        if not privacy:
            messages.error(request,"Please Accept Privacy Policy")
            return render(request,'home/signup.html', context)
        myuser=User.objects.create_user(username=username,email=email,password=pass1,name=name,role=role,verified=verified,onboarding_completed=False)
        myuser.save()
        messages.success(request,"Your Articlio Account Is Successfully Created")
        login(request,authenticate(username=username,password=pass1))
        nextUrl = request.POST.get('next')
        if nextUrl:
            return redirect(nextUrl)
        return redirect('onboarding')
    return render(request,'home/signup.html')

def handleLogin(request):
    if request.method=='POST':
        loginusername=request.POST['loginusername']
        loginpass=request.POST['loginpass']
        user=authenticate(username=loginusername,password=loginpass)
        if user is not None:
            login(request,user)
            messages.success(request,"Successfully Logged In")
            nextUrl = request.POST.get('next')
            if nextUrl:
                return redirect(nextUrl)
            if not user.onboarding_completed:
                return redirect('onboarding')
            return redirect('home')
        else:
            messages.error(request,"Invalid Credentials")
            return render(request,'home/login.html', {'loginusername': loginusername})
    return render(request,'home/login.html')

def handleLogout(request):
    nextUrl=request.GET.get('next')
    logout(request)
    messages.success(request,"Successfully Logged Out")
    if nextUrl:
        return redirect(nextUrl)
    return redirect('home')
    

def terms(request):
    return render(request,'home/terms.html')

def privacy(request):
    return render(request,'home/privacy.html')


def resetPassword(request):
    
    if request.method == "GET":
        stored_code = request.session.get('email_verification_code')
        stored_email = request.session.get('email_verification_email')
        stored_username = request.session.get('email_verification_username')
        stored_time = request.session.get('email_verification_time')

        # If there is a valid verification session active, show the verify step
        if stored_code and stored_email and stored_username and stored_time and (time.time() - stored_time <= 1800):
            return render(request, 'home/forgetPassword.html', {
                "step": "verify",
                "username": stored_username,
                "email": stored_email,
            })

        return render(request, 'home/forgetPassword.html', {
            "step": "send",
        })

    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        user = User.objects.filter(username=username, email=email).first()
        if not user:
            messages.error(request, "User does not exist")
            return render(request, 'home/forgetPassword.html', {
                "step": "send",
                "username": username,
                "email": email,
            })
        
        action = request.POST.get('action')

        if action == 'resend' or 'emailcode' not in request.POST:
            verification_code = str(random.randint(100000, 999999))

            request.session['email_verification_code'] = verification_code
            request.session['email_verification_email'] = email
            request.session['email_verification_username'] = username
            request.session['email_verification_time'] = time.time()
            request.session.modified = True

            send_verification_email(user, verification_code, 'reset_password', request)

            messages.success(request, "Verification code sent to your email")

            # Redirect to GET to prevent resending code on page refresh
            return redirect(reverse('resetPassword'))

        entered_code = request.POST.get('emailcode')
        stored_code = request.session.get('email_verification_code')
        stored_email = request.session.get('email_verification_email')
        stored_time = request.session.get('email_verification_time')
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')

        # Validate that verification session is not expired (30 minutes)
        if not stored_code or stored_email != email or not stored_time or (time.time() - stored_time > 1800):
            messages.error(request, "Verification session expired. Please try again.")
            request.session.pop('email_verification_code', None)
            request.session.pop('email_verification_email', None)
            request.session.pop('email_verification_username', None)
            request.session.pop('email_verification_time', None)
            request.session.modified = True
            redirect_url = reverse('resetPassword')
            return redirect(redirect_url)

        if entered_code != stored_code:
            messages.error(request, "Invalid verification code")
            return render(request, 'home/forgetPassword.html', {
                "step": "verify","username":username,"email":email
            })
        
        if pass1!=pass2:
            messages.error(request,"Password Do Not Match")
            return render(request, 'home/forgetPassword.html', {
                "step": "verify","username":username,"email":email
            })

        request.session.pop('email_verification_code', None)
        request.session.pop('email_verification_email', None)
        request.session.pop('email_verification_username', None)
        request.session.pop('email_verification_time', None)
        request.session.modified = True

        user = User.objects.get(username=username,email=email)
        user.set_password(pass1)
        user.save()
        messages.success(request, "Password reset successfully")
        
        return redirect('handleLogin')

def complete_profile(request):
    """Profile-completion page shown to first-time OAuth users."""
    if not request.user.is_authenticated:
        return redirect('handleLogin')

    # If profile is already completed, go home
    if request.user.social_profile_completed:
        return redirect('home')

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        username = request.POST.get('username', '').strip()
        role = request.POST.get('role', 'reader')

        # Validation
        if not name or len(name) < 2:
            messages.error(request, "Name must be at least 2 characters.")
            return render(request, 'home/complete_profile.html')

        if not username:
            messages.error(request, "Username is required.")
            return render(request, 'home/complete_profile.html')

        if len(username) > 10:
            messages.error(request, "Username must be less than 10 characters.")
            return render(request, 'home/complete_profile.html')

        if not username.isalnum():
            messages.error(request, "Username should contain letters and numbers only.")
            return render(request, 'home/complete_profile.html')

        # Check uniqueness (excluding current user)
        if User.objects.filter(username=username).exclude(pk=request.user.pk).exists():
            messages.error(request, "That username is already taken.")
            return render(request, 'home/complete_profile.html')

        if role not in ('reader', 'author'):
            role = 'reader'

        user = request.user
        user.name = name
        user.username = username
        user.role = role
        user.verified = True
        user.social_profile_completed = True
        user.save()

        messages.success(request, "Profile completed! Welcome to Articlio.")
        return redirect('home')

    return render(request, 'home/complete_profile.html')

def update_theme_preference(request):
    if request.method == 'POST' and request.user.is_authenticated:
        try:
            data = json.loads(request.body)
            theme = data.get('theme')
            if theme:
                user = request.user
                user.theme_preference = theme
                user.save(update_fields=['theme_preference'])
                return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

def check_username_availability(request):
    """
    API endpoint to check if a username is available in real-time.
    Uses our custom Bloom Filter for extreme speed.
    """
    username = request.GET.get('username', '').strip().lower()
    
    if not username:
        return JsonResponse({'error': 'No username provided'}, status=400)
        
    if not username.isalnum() or len(username) > 10:
        return JsonResponse({'available': False, 'message': 'Invalid format'})
        
    # Get the Bloom filter (from cache or reconstructs it)
    from home.utils import get_username_bloom_filter
    bf = get_username_bloom_filter()
    
    # Check the Bloom filter FIRST!
    is_probably_taken = bf.check(username)
    
    if not is_probably_taken:
        # Bloom Filter says NO? It is DEFINITELY available. No database hit needed!
        return JsonResponse({'available': True, 'message': 'Available!'})
    else:
        # Bloom Filter says YES? It MIGHT be taken. We must check the database to be sure.
        # This resolves any False Positives.
        is_actually_taken = User.objects.filter(username__iexact=username).exists()
        
        if is_actually_taken:
            return JsonResponse({'available': False, 'message': 'Already taken'})
        else:
            # False positive! It's actually available.
            return JsonResponse({'available': True, 'message': 'Available!'})

# ── PROFILES & FOLLOW SYSTEM VIEWS ──

from django.db.models import Sum, Q
from blog.models import Post
from home.models import CustomUser, Follow
from django.core.paginator import Paginator, EmptyPage
from django.views.decorators.http import require_POST

def profile(request, username=None):
    if username is None:
        if not request.user.is_authenticated:
            return redirect('handleLogin')
        user = request.user
        is_own_profile = True
    else:
        user = get_object_or_404(CustomUser, username=username)
        is_own_profile = (request.user.is_authenticated and request.user.username == user.username)
        if is_own_profile:
            return redirect('profile')

    # Calculate stats
    user_posts = Post.objects.filter(Q(author_user=user) | Q(author_user__isnull=True, author=user.name))
    total_posts = user_posts.count()
    total_views = user_posts.aggregate(Sum('views'))['views__sum'] or 0
    total_likes = user_posts.aggregate(Sum('likes'))['likes__sum'] or 0
    
    followers_count = Follow.objects.filter(followed=user).count()
    following_count = Follow.objects.filter(follower=user).count()
    
    is_following = False
    if request.user.is_authenticated and not is_own_profile:
        is_following = Follow.objects.filter(follower=request.user, followed=user).exists()
        
    written_categories = list(user_posts.filter(draft=False).values_list('category', flat=True).distinct())
    
    all_categories_qs = Post.objects.filter(draft=False).values_list('category', flat=True).distinct()
    all_categories = sorted(list(set(list(all_categories_qs) + ['technology', 'design', 'development', 'productivity', 'general'])))
    
    followed_relations = Follow.objects.filter(follower=user).select_related('followed')
    followed_authors = [rel.followed for rel in followed_relations]
    
    follower_relations = Follow.objects.filter(followed=user).select_related('follower')
    followers_list = [rel.follower for rel in follower_relations]
    
    user_interests = [i.strip() for i in user.interests.split(',') if i.strip()] if user.interests else []

    context = {
        'profile_user': user,
        'is_own_profile': is_own_profile,
        'total_posts': total_posts,
        'total_views': total_views,
        'total_likes': total_likes,
        'followers_count': followers_count,
        'following_count': following_count,
        'is_following': is_following,
        'written_categories': written_categories,
        'all_categories': all_categories,
        'followed_authors': followed_authors,
        'followers_list': followers_list,
        'user_interests': user_interests,
    }
    return render(request, 'home/profile.html', context)

@require_POST
def toggle_follow(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    try:
        data = json.loads(request.body)
        username_to_follow = data.get('username')
        target_user = get_object_or_404(CustomUser, username=username_to_follow)
        
        if target_user == request.user:
            return JsonResponse({'error': 'You cannot follow yourself'}, status=400)
            
        follow_rel = Follow.objects.filter(follower=request.user, followed=target_user)
        if follow_rel.exists():
            follow_rel.delete()
            following = False
        else:
            Follow.objects.create(follower=request.user, followed=target_user)
            following = True
            
        followers_count = Follow.objects.filter(followed=target_user).count()
        following_count = Follow.objects.filter(follower=request.user).count()
        
        return JsonResponse({
            'status': 'success',
            'following': following,
            'followers_count': followers_count,
            'following_count': following_count
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_POST
def update_profile(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            bio = data.get('bio', '')
            profile_picture_url = data.get('profile_picture_url', '')
            github_url = data.get('github_url', '')
            twitter_url = data.get('twitter_url', '')
            linkedin_url = data.get('linkedin_url', '')
            website_url = data.get('website_url', '')
            interests_list = data.get('interests', [])
            interests = ','.join(interests_list)
        else:
            bio = request.POST.get('bio', '')
            profile_picture_url = request.POST.get('profile_picture_url', '')
            github_url = request.POST.get('github_url', '')
            twitter_url = request.POST.get('twitter_url', '')
            linkedin_url = request.POST.get('linkedin_url', '')
            website_url = request.POST.get('website_url', '')
            interests_list = request.POST.getlist('interests')
            interests = ','.join(interests_list)
            
        user = request.user
        user.bio = bio
        user.profile_picture_url = profile_picture_url
        if not request.content_type == 'application/json' and request.FILES.get('profile_picture'):
            user.profile_picture = request.FILES.get('profile_picture')
        user.github_url = github_url
        user.twitter_url = twitter_url
        user.linkedin_url = linkedin_url
        user.website_url = website_url
        user.interests = interests
        user.save()
        
        if request.content_type == 'application/json':
            return JsonResponse({'status': 'success'})
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    except Exception as e:
        if request.content_type == 'application/json':
            return JsonResponse({'error': str(e)}, status=400)
        messages.error(request, f'Failed to update profile: {e}')
        return redirect('profile')

def api_author_posts(request, username):
    author = get_object_or_404(CustomUser, username=username)
    
    sort_by = request.GET.get('sort_by', '-timestamp')
    valid_sorts = ['timestamp', '-timestamp', 'views', '-views', 'likes', '-likes']
    if sort_by not in valid_sorts:
        sort_by = '-timestamp'
        
    all_posts = Post.objects.filter(Q(author_user=author) | Q(author_user__isnull=True, author=author.name), draft=False).order_by(sort_by)
    
    from django.db.models import Subquery, OuterRef
    max_views_subquery = Post.objects.filter(
        draft=False, category=OuterRef('category')
    ).order_by('-views').values('views')[:1]
    trending_post_ids = set(Post.objects.filter(
        draft=False,
        views=Subquery(max_views_subquery)
    ).values_list('sno', flat=True))
    
    from django.utils import timezone
    
    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        page = 1
        
    paginator = Paginator(all_posts, 6)
    try:
        page_obj = paginator.page(page)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages) if paginator.num_pages > 0 else []
        
    posts_data = []
    for p in page_obj:
        posts_data.append({
            'sno': p.sno,
            'title': p.title,
            'summary': p.summary,
            'slug': p.slug,
            'category': p.category,
            'views': p.views,
            'likes': p.likes,
            'reading_time': p.reading_time,
            'timestamp': p.timestamp.strftime('%b. %d, %Y'),
            'is_new': (timezone.now() - p.timestamp).days <= 7 if p.timestamp else False,
            'is_trending': p.sno in trending_post_ids,
        })
        
    return JsonResponse({
        'posts': posts_data,
        'page': page_obj.number if page_obj else 1,
        'total_pages': paginator.num_pages,
        'has_next': page_obj.has_next() if page_obj else False,
        'total_posts': paginator.count
    })


def api_profile_followers(request, username):
    user = get_object_or_404(CustomUser, username=username)
    follower_relations = Follow.objects.filter(followed=user).select_related('follower')
    followers_data = []
    for rel in follower_relations:
        follower = rel.follower
        avatar_url = ''
        if follower.profile_picture:
            avatar_url = follower.profile_picture.url
        elif follower.profile_picture_url:
            avatar_url = follower.profile_picture_url
            
        followers_data.append({
            'username': follower.username,
            'name': follower.name,
            'avatar_url': avatar_url,
        })
    return JsonResponse({'followers': followers_data})


def api_profile_following(request, username):
    user = get_object_or_404(CustomUser, username=username)
    followed_relations = Follow.objects.filter(follower=user).select_related('followed')
    following_data = []
    for rel in followed_relations:
        author = rel.followed
        avatar_url = ''
        if author.profile_picture:
            avatar_url = author.profile_picture.url
        elif author.profile_picture_url:
            avatar_url = author.profile_picture_url
            
        following_data.append({
            'username': author.username,
            'name': author.name,
            'avatar_url': avatar_url,
        })
    return JsonResponse({'following': following_data})


# ── ONBOARDING VIEWS ──

def onboarding(request):
    """New user onboarding: category selection + author suggestions."""
    if not request.user.is_authenticated:
        return redirect('handleLogin')
    if request.user.onboarding_completed:
        return redirect('home')

    if request.method == 'POST':
        interests_list = request.POST.getlist('interests')
        follow_usernames = request.POST.getlist('follow_authors')

        user = request.user
        user.interests = ','.join(interests_list)
        user.onboarding_completed = True
        user.save(update_fields=['interests', 'onboarding_completed'])

        # Create follow relationships
        for uname in follow_usernames:
            try:
                target = CustomUser.objects.get(username=uname)
                if target != user:
                    Follow.objects.get_or_create(follower=user, followed=target)
            except CustomUser.DoesNotExist:
                continue

        messages.success(request, "Welcome to Articlio! Your feed is personalized.")
        return redirect('home')

    all_categories_qs = Post.objects.filter(draft=False).values_list('category', flat=True).distinct()
    all_categories = sorted(list(set(list(all_categories_qs) + ['technology', 'design', 'development', 'productivity', 'general'])))

    return render(request, 'home/onboarding.html', {
        'all_categories': all_categories,
    })


def api_suggested_authors(request):
    """Return top 3 most-followed authors per selected category."""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    categories = request.GET.getlist('categories')
    if not categories:
        return JsonResponse({'authors': []})

    from django.db.models import Count

    # Find authors who write in the selected categories, ordered by follower count
    authors_in_categories = (
        CustomUser.objects.filter(
            role='author',
            posts__draft=False,
            posts__category__in=categories
        )
        .exclude(pk=request.user.pk)
        .annotate(follower_count=Count('follower_relations', distinct=True))
        .order_by('-follower_count')
        .distinct()[:9]  # Top 9 unique authors across all selected categories
    )

    authors_data = []
    seen = set()
    for author in authors_in_categories:
        if author.username in seen:
            continue
        seen.add(author.username)

        avatar_url = ''
        if author.profile_picture:
            avatar_url = author.profile_picture.url
        elif author.profile_picture_url:
            avatar_url = author.profile_picture_url

        # Get categories this author writes in (from selected ones)
        author_cats = list(
            Post.objects.filter(author_user=author, draft=False, category__in=categories)
            .values_list('category', flat=True).distinct()
        )

        authors_data.append({
            'username': author.username,
            'name': author.name,
            'bio': (author.bio or '')[:120],
            'avatar_url': avatar_url,
            'follower_count': author.follower_count,
            'categories': author_cats,
        })

    return JsonResponse({'authors': authors_data})