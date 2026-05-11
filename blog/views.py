from django.shortcuts import render,redirect,get_object_or_404
from .models import Post,BlogComment,Like,Bookmark
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import JsonResponse
import json
import random
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.text import slugify
from . import sanitizer
from django.utils.html import strip_tags
from textwrap import shorten
import re


def blogHome(request):
    allPosts=Post.objects.filter(draft=False)
    authors=Post.objects.filter(draft=False).values('author').distinct()
    categories=Post.objects.filter(draft=False).values('category').distinct()
    if request.user.is_authenticated:
        bookmarked = set(Bookmark.objects.filter(user=request.user).values_list('post_id', flat=True))
    else:
        bookmarked = set()
    context={'allPosts':allPosts,'filter':'all','authors':authors,'selectedAuthor':'all','selectedCategory':'all','categories':categories,'bookmarked':bookmarked}
    return render(request,'blog/blogHome.html',context)

def filteredBlogs(request):
    allPosts=Post.objects.filter(draft=False)
    authors=Post.objects.filter(draft=False).values('author').distinct()
    categories=Post.objects.filter(draft=False).values('category').distinct()
    filtered=request.GET.get("filter")
    authorsFilter=request.GET.get("authors")
    categoryFilter=request.GET.get("category")
    if request.user.is_authenticated:
        bookmarked = set(Bookmark.objects.filter(user=request.user).values_list('post_id', flat=True))
    else:
        bookmarked = set()
    if filtered=="all" and authorsFilter=="all" and categoryFilter=="all":
        return redirect('blogHome')
    elif filtered=="liked":
        allPosts=allPosts.order_by('-likes')
    elif filtered=="unliked":
        allPosts=allPosts.order_by('likes')
    elif filtered=="viewed":
        allPosts=allPosts.order_by('-views')
    elif filtered=="unviewed":
        allPosts=allPosts.order_by('views')
    elif filtered=="latest":
        allPosts=allPosts.order_by('-timestamp')
    elif filtered=="old":
        allPosts=allPosts.order_by('timestamp')

    if authorsFilter!="all":
        allPosts=allPosts.filter(author=authorsFilter)
    if categoryFilter!="all":
        allPosts=allPosts.filter(category=categoryFilter)
    return render(request,'blog/blogHome.html',{'allPosts':allPosts,'filter':filtered,'authors':authors,'selectedAuthor':authorsFilter,'selectedCategory':categoryFilter,'categories':categories,'bookmarked':bookmarked})

def bookmarks(request):
    if request.user.is_authenticated:
        savedPost = Post.objects.filter(bookmark__user=request.user).distinct() 
        bookmarked = set(Bookmark.objects.filter(user=request.user).values_list('post_id', flat=True))
        return render(request,'blog/bookmarkBlog.html',{'allPosts':savedPost,'bookmarked':bookmarked})
    else:
        return redirect('blogHome')

def blogPost(request,slug):
    post=Post.objects.filter(slug=slug,draft=False).first()
    interestedPosts=Post.objects.filter(draft=False,category=post.category).exclude(sno=post.sno)[:4]
    viewed_posts = request.session.get("viewed_posts", [])
    if post.sno not in viewed_posts:
        post.views += 1
        post.save(update_fields=["views"])

        viewed_posts.append(post.sno)
        request.session["viewed_posts"] = viewed_posts
        request.session.modified = True
    post.save()
    comments=BlogComment.objects.filter(post=post,parent=None)
    replies=BlogComment.objects.filter(post=post).exclude(parent=None)
    repDict={}
    for reply in replies:
        if reply.parent.sno not in repDict.keys():
            repDict[reply.parent.sno]=[reply]
        else:
            repDict[reply.parent.sno].append(reply)
    if request.user.is_authenticated:
        context={'post':post,"comments":comments,"user":request.user,'repDict':repDict,'liked':Like.objects.filter(post=post.sno,user=request.user).exists(),'bookmarked':Bookmark.objects.filter(post=post.sno,user=request.user).exists(),'interestedPosts':interestedPosts}
    else:
        context={'post':post,"comments":comments,'repDict':repDict,'liked':False,'interestedPosts':interestedPosts}
    return render(request,'blog/blogPost.html',context)

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
        draftBlogs=Post.objects.filter(author=request.user.name,draft=True).order_by('-updated_at')
        postedBlogs=Post.objects.filter(author=request.user.name,draft=False).order_by('-updated_at')
        return render(request,'blog/myBlogs.html',{'draftBlogs':draftBlogs,'postedBlogs':postedBlogs})
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
    data = json.loads(request.body)
    post_id = data.get("post_id")
    request_timestamp = data.get("timestamp", 0)
    post = Post.objects.get(sno=post_id)

    if request.user.is_authenticated:
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
    else:
        return JsonResponse({
            "status": "unknown",
            "likes": post.likes,
            "timestamp": request_timestamp
        })
    
@require_POST
def toggle_bookmark(request):
    data = json.loads(request.body)
    post_id = data.get("post_id")
    request_timestamp = data.get("timestamp")
    post = Post.objects.get(sno=post_id)

    if request.user.is_authenticated:
        user = request.user

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
    else:
        return JsonResponse({
            "status": "unsave",
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
        return render(request, 'blog/emailVerification.html', {
            "step": "send",
            "next": next_url
        })

    if request.method == "POST":

        if 'emailcode' not in request.POST:

            verification_code = str(random.randint(100000, 999999))

            request.session['email_verification_code'] = verification_code
            request.session['email_verification_email'] = request.user.email
            request.session.modified = True

            send_mail(
                subject="Articlio Email Verification Code",
                message=f"Your verification code is: {verification_code}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[request.user.email],
                fail_silently=False,
            )

            messages.success(request, "Verification code sent to your email")

            return render(request, 'blog/emailVerification.html', {
                "step": "verify",
                "next": next_url
            })
        entered_code = request.POST.get('emailcode')
        stored_code = request.session.get('email_verification_code')
        stored_email = request.session.get('email_verification_email')

        if not stored_code or stored_email != request.user.email:
            messages.error(request, "Verification session expired. Please try again.")
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
        request.session.modified = True

        messages.success(request, "Email verified successfully")

        return redirect(next_url or 'home')
