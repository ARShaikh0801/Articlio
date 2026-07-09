from django.shortcuts import render,redirect,get_object_or_404
from .models import Post,BlogComment,Like,Bookmark,Reaction
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.db.models import F, Sum
from django.db import transaction
import json
import random
import time
from home.utils import send_verification_email

from django.core.mail import send_mail
from django.urls import reverse
from django.utils.text import slugify
from . import sanitizer
from django.utils.html import strip_tags
from textwrap import shorten
import re


def blogHome(request):
    """
    Renders the main blog homepage showing all posts, authors, and categories.
    """
    return render(request, 'blog/blogHome.html', {'filter': 'all', 'selectedAuthor': 'all', 'selectedCategory': 'all'})

def filteredBlogs(request):
    """
    Filters and renders the blog list page based on request query parameters.
    """
    filtered = request.GET.get("filter", "all")
    authorsFilter = request.GET.get("authors", "all")
    categoryFilter = request.GET.get("category", "all")
    return render(request, 'blog/blogHome.html', {'filter': filtered, 'selectedAuthor': authorsFilter, 'selectedCategory': categoryFilter})

def bookmarks(request):
    """
    Renders the page containing the user's bookmarked blog posts.
    """
    if request.user.is_authenticated:
        return render(request, 'blog/bookmarkBlog.html')
    else:
        return redirect('blogHome')

def history(request):
    """
    Renders the page containing the user's reading history.
    """
    return render(request, 'blog/historyBlog.html')

def blogPost(request,slug):
    """
    Renders the full post view for a specific article. Increments the view count
    if the user is opening it for the first time in their active session.
    """
    post=get_object_or_404(Post, slug=slug, draft=False)
    
    viewed_posts = request.session.get("viewed_posts", [])
    if post.sno not in viewed_posts:
        post.views += 1
        post.save(update_fields=["views"])

        viewed_posts.append(post.sno)
        request.session["viewed_posts"] = viewed_posts
        request.session.modified = True
        
    return render(request,'blog/blogPost.html', {'post': post})

def generate_unique_slug(model, base_text):
    base_slug = slugify(base_text)
    slug = base_slug
    counter = 1

    while model.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug

def generate_summary(html, length=200):
   
    text = strip_tags(html)

    text = re.sub(r'\s+', ' ', text).strip()

    return shorten(text, width=length, placeholder='…')

def writeBlog(request):
    if not request.user.is_authenticated:
        messages.warning(request,"Login To Post Blog...")
        return redirect('blogHome')
    else:
        if request.user.role != 'author':
            messages.error(request,"Only Authors can Post Blogs ! ")
            return redirect('blogHome')
        elif request.user.verified==False:
            messages.warning(request,"Please Verify Your Account To Post Blogs !")
            return redirect('emailVerification')
        else:
            if request.method=="POST":
                title=request.POST.get('title')
                category=request.POST.get('category')
                content=request.POST.get('content')
                if title=="" or category=="" or content=="":
                    if request.POST.get('is_autosave') == 'true':
                        return JsonResponse({'status': 'error', 'message': 'Incomplete fields'})
                    messages.error(request,"All Fields Are Required !")
                    return redirect('writeBlog')
                content=sanitizer.sanitize_html(content)
                content=sanitizer.normalize_links(content)
                summary = generate_summary(content)
                slug = generate_unique_slug(Post, title)
                author=request.user.name
                draft = request.POST.get('draftVal') == "true"
                existedSlug=request.POST.get('slug','')
                if existedSlug!="":
                    post=Post.objects.filter(slug=existedSlug).first()
                    post.title=title
                    post.category=category
                    post.content=content
                    post.summary=summary
                    post.author=author
                    post.slug=slug
                    post.draft=draft
                    post.save()
                else:
                    post=Post(title=title,category=category,content=content,summary=summary,author=author,slug=slug,draft=draft)
                    post.save()
                if request.POST.get('is_autosave') == 'true':
                    return JsonResponse({'status': 'success', 'slug': post.slug})

                if draft:
                    messages.success(request,"Draft Saved Successfully")
                else:
                    messages.success(request,"Blog Posted Successfully")
                return redirect('myBlogs')
    return render(request,'blog/writeBlog.html')

def myBlogs(request):
    if request.user.is_authenticated:
        if request.user.role != 'author':
            messages.error(request,"Only Authors can Post Blogs ! ")
            return redirect('blogHome')
        elif request.user.verified==False:
            messages.error(request,"Please Verify Your Account First !")
            return redirect('blogHome')
        return render(request,'blog/myBlogs.html')
    else:
        return redirect('blogHome')

def editBlogPost(request,slug): 
    if request.method=="POST":
        post=Post.objects.filter(slug=slug,author=request.user.name).first()
        context={'post':post}
        return render(request,'blog/writeBlog.html',context)
    else:
        return redirect('blogHome')

@require_POST
def deleteBlogPost(request, slug):
    blog = get_object_or_404(Post, slug=slug, author=request.user.name)
    blog.delete()
    messages.success(request, "Blog Deleted Successfully")
    return redirect("myBlogs")


from django.db import IntegrityError
from django.db.models import F
from django.db.models.functions import Greatest

@require_POST
def toggle_like(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    data = json.loads(request.body)
    post_id = data.get("post_id")
    request_timestamp = data.get("timestamp", 0)
    post = Post.objects.get(sno=post_id)
    user = request.user

    # Server-side timestamp enforcement - reject stale requests
    ts_key = f'like_ts_{post_id}'
    last_ts = request.session.get(ts_key, 0)
    if request_timestamp and request_timestamp <= last_ts:
        post.refresh_from_db()
        liked = Like.objects.filter(post=post, user=user).exists()
        return JsonResponse({
            "status": "liked" if liked else "unliked",
            "likes": post.likes,
            "timestamp": request_timestamp
        })
    request.session[ts_key] = request_timestamp
    request.session.modified = True

    # Atomic delete - avoids TOCTOU race
    deleted_count, _ = Like.objects.filter(post=post, user=user).delete()
    if deleted_count > 0:
        Post.objects.filter(sno=post_id).update(likes=Greatest(F('likes') - 1, 0))
        status = "unliked"
    else:
        try:
            Like.objects.create(post=post, user=user)
            Post.objects.filter(sno=post_id).update(likes=F('likes') + 1)
            status = "liked"
        except IntegrityError:
            # Race condition: someone already created the like
            status = "liked"

    # Fetch fresh count after update
    post.refresh_from_db()

    return JsonResponse({
        "status": status,
        "likes": post.likes,
        "timestamp": request_timestamp
    })
    
@require_POST
def toggle_bookmark(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    data = json.loads(request.body)
    post_id = data.get("post_id")
    request_timestamp = data.get("timestamp")
    post = Post.objects.get(sno=post_id)
    user = request.user

    # Server-side timestamp enforcement - reject stale requests
    ts_key = f'bookmark_ts_{post_id}'
    last_ts = request.session.get(ts_key, 0)
    if request_timestamp and request_timestamp <= last_ts:
        bookmarked = Bookmark.objects.filter(post=post, user=user).exists()
        return JsonResponse({
            "status": "save" if bookmarked else "unsave",
            "timestamp": request_timestamp
        })
    request.session[ts_key] = request_timestamp
    request.session.modified = True

    # Atomic delete - avoids TOCTOU race
    deleted_count, _ = Bookmark.objects.filter(post=post, user=user).delete()
    if deleted_count > 0:
        status = "unsave"
    else:
        try:
            Bookmark.objects.create(post=post, user=user)
            status = "save"
        except IntegrityError:
            status = "save"

    return JsonResponse({
        "status": status,
        "timestamp": request_timestamp
    })
    
@require_POST
def postComment(request):
    try:
        data = json.loads(request.body)
        comment_text = data.get("comment", "")
        if comment_text == "":
            return JsonResponse({"status": "error", "message": "Comment Field Is Required !"}, status=400)
            
        comment_text = sanitizer.sanitize_comment(comment_text)
        user = request.user
        postSno = data.get("postSno")
        post = Post.objects.get(sno=postSno)
        parentSno = data.get("parentSno")
        
        if not parentSno:
            comments = BlogComment(comment=comment_text, user=user, post=post)
            comments.save()
            return JsonResponse({"status": "success", "message": "Comment Posted Successfully", "comment_sno": comments.sno})
        else:
            parent = BlogComment.objects.get(sno=parentSno)
            comments = BlogComment(comment=comment_text, user=user, post=post, parent=parent)
            comments.save()
            return JsonResponse({"status": "success", "message": "Reply Posted Successfully", "comment_sno": comments.sno})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


def emailVerification(request):
    
    next_url = request.POST.get('next') or request.GET.get('next')
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to verify your email.")
        return redirect(next_url or 'home')
    
    if request.user.verified and request.user.role == "author":
        messages.success(request, "Your email is already verified.")
        return redirect(next_url or 'home')

    if request.user.role != "author":
        messages.error(request, "No verification required for readers.")
        return redirect(next_url or 'home')

    if request.method == "GET":
        stored_code = request.session.get('email_verification_code')
        stored_email = request.session.get('email_verification_email')
        stored_time = request.session.get('email_verification_time')

        # If there is a valid verification code in the session, show the verify step
        if stored_code and stored_email == request.user.email and stored_time and (time.time() - stored_time <= 1800):
            return render(request, 'blog/emailVerification.html', {
                "step": "verify",
                "next": next_url
            })

        return render(request, 'blog/emailVerification.html', {
            "step": "send",
            "next": next_url
        })

    if request.method == "POST":
        action = request.POST.get('action')

        if action == 'resend' or 'emailcode' not in request.POST:
            verification_code = str(random.randint(100000, 999999))

            request.session['email_verification_code'] = verification_code
            request.session['email_verification_email'] = request.user.email
            request.session['email_verification_time'] = time.time()
            request.session.modified = True

            send_verification_email(request.user, verification_code, 'verify_email', request)

            messages.success(request, "Verification code sent to your email")

            # Redirect to GET to prevent resending code on page refresh
            redirect_url = reverse('emailVerification')
            if next_url:
                redirect_url += f"?next={next_url}"
            return redirect(redirect_url)

        entered_code = request.POST.get('emailcode')
        stored_code = request.session.get('email_verification_code')
        stored_email = request.session.get('email_verification_email')
        stored_time = request.session.get('email_verification_time')

        # Validate that verification session is not expired (30 minutes)
        if not stored_code or stored_email != request.user.email or not stored_time or (time.time() - stored_time > 1800):
            messages.error(request, "Verification session expired. Please try again.")
            request.session.pop('email_verification_code', None)
            request.session.pop('email_verification_email', None)
            request.session.pop('email_verification_time', None)
            request.session.modified = True
            redirect_url = reverse('emailVerification')
            if next_url:
                redirect_url += f"?next={next_url}"
            return redirect(redirect_url)

        if entered_code != stored_code:
            messages.error(request, "Invalid verification code")
            return render(request, 'blog/emailVerification.html', {
                "step": "verify",
                "next": next_url
            })

        request.user.verified = True
        request.user.save(update_fields=['verified'])

        request.session.pop('email_verification_code', None)
        request.session.pop('email_verification_email', None)
        request.session.pop('email_verification_time', None)
        request.session.modified = True

        messages.success(request, "Email verified successfully")

        return redirect(next_url or 'home')

@require_POST
def toggle_comment_like(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    try:
        data = json.loads(request.body)
        comment_id = data.get("comment_id")
        comment = BlogComment.objects.get(sno=comment_id)
        user = request.user

        if comment.likes.filter(id=user.id).exists():
            comment.likes.remove(user)
            status = "unliked"
        else:
            comment.likes.add(user)
            status = "liked"

        return JsonResponse({
            "status": status,
            "likes_count": comment.likes.count()
        })
    except BlogComment.DoesNotExist:
        return JsonResponse({"error": "Comment not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@require_POST
def add_reactions_batch(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    try:
        data = json.loads(request.body)
        post_id = data.get("post_id")
        increments = data.get("increments", {})
        post = Post.objects.get(sno=post_id)
        user = request.user

        valid_types = ['fire', 'insightful', 'celebrate', 'surprised']

        with transaction.atomic():
            for r_type, inc in increments.items():
                if r_type not in valid_types:
                    continue
                try:
                    inc = int(inc)
                except (ValueError, TypeError):
                    continue
                if inc <= 0:
                    continue

                reaction, created = Reaction.objects.get_or_create(
                    post=post, user=user, type=r_type,
                    defaults={'count': 0}
                )
                reaction.count = F('count') + inc
                reaction.save()

        # Retrieve final aggregated totals and user counts in 2 bulk queries
        totals = {r_type: 0 for r_type in valid_types}
        user_counts = {r_type: 0 for r_type in valid_types}

        totals_qs = Reaction.objects.filter(post=post, type__in=valid_types).values('type').annotate(total=Sum('count'))
        for row in totals_qs:
            totals[row['type']] = row['total'] or 0

        user_qs = Reaction.objects.filter(post=post, user=user, type__in=valid_types).values('type', 'count')
        for row in user_qs:
            user_counts[row['type']] = row['count'] or 0

        return JsonResponse({
            "status": "success",
            "reactions": totals,
            "user_reactions": user_counts
        })
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

