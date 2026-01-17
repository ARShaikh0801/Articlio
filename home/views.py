from django.shortcuts import render,HttpResponse,redirect
from django.contrib import messages
from home.models import Contact
from blog.models import Post,Bookmark
from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib.auth import authenticate,login,logout
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
import random

def home(request):
    topPosts=Post.objects.filter(draft=False).order_by('-views')[:2]
    if(request.user.is_authenticated): 
        bookmarked = set(Bookmark.objects.filter(user=request.user).values_list('post_id', flat=True))
    else:
        bookmarked = set()
    context={'topPosts':topPosts,'bookmarked':bookmarked}
    return render(request,'home/home.html',context)

def contact(request):
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
    return render(request,'home/about.html')

def search(request):
    query=request.GET.get('query')
    if query=='':
        return redirect('blogHome')
    else:
        if(request.user.is_authenticated): 
            bookmarked = set(Bookmark.objects.filter(user=request.user).values_list('post_id', flat=True))
        else:
            bookmarked = set()
        if len(query)>30:
            messages.warning(request,"Please Enter Less Than 30 Character")
            allPosts=Post.objects.none()
        
        else:
            allPostsTitle=Post.objects.filter(title__icontains=query,draft=False)
            allPostsCategory=Post.objects.filter(category__icontains=query,draft=False)
            allPostsContent=Post.objects.filter(content__icontains=query,draft=False)
            allPostsAuthor=Post.objects.filter(author__icontains=query,draft=False)
            allPosts=allPostsTitle.union(allPostsContent,allPostsAuthor,allPostsCategory).order_by('-views')

            if allPosts.count()==0:
                messages.warning(request,"No Search Result Found")

    context={'allPosts':allPosts,'query':query,'bookmarked':bookmarked}
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
        if not (username and name and email and role and pass1 and pass2 and verifiedstr):
            messages.error(request,"All Fields Are Compulsory")
            return render(request,'home/signup.html')
        if verifiedstr=='False':
            verified=False
        else:
            verified=True
        if len(username)>10:
            messages.error(request,"Username Must Be Less Than 10 Character")
            return render(request,'home/signup.html')
        if not username.isalnum():
            messages.error(request,"Username Should Contain Letters And Numbers Only")
            return render(request,'home/signup.html')
        if pass1!=pass2:
            messages.error(request,"Password Do Not Match")
            return render(request,'home/signup.html')
        if User.objects.filter(username=username,email=email).exists():
            messages.error(request,"Account Already Exists Please Login")
            return render(request,'home/signup.html')
        if User.objects.filter(username=username).exists():
            messages.error(request,"Username Already Exists")
            return render(request,'home/signup.html')
        if User.objects.filter(email=email).exists():
            messages.error(request,"Email Already Exists")
            return render(request,'home/signup.html')
        if not terms:
            messages.error(request,"Please Accept Terms And Conditions")
            return render(request,'home/signup.html')
        if not privacy:
            messages.error(request,"Please Accept Privacy Policy")
            return render(request,'home/signup.html')
        myuser=User.objects.create_user(username=username,email=email,password=pass1,name=name,role=role,verified=verified)
        myuser.save()
        messages.success(request,"Your Articlio Account Is Successfully Created")
        login(request,authenticate(username=username,password=pass1))
        nextUrl = request.POST.get('next')
        if nextUrl:
            return redirect(nextUrl)
        return redirect('home')
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
            return redirect('home')
        else:
            messages.error(request,"Invalid Credentials")
            return render(request,'home/login.html')
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
        return render(request, 'home/forgetPassword.html', {
            "step": "send",
        })

    if request.method == "POST":
        username=request.POST.get('username')
        email=request.POST.get('email')
        userExists = User.objects.filter(username=username,email=email).exists()
        if not userExists:
            messages.error(request, "User does not exist")
            return render(request, 'home/forgetPassword.html', {
                "step": "send",
            })
        
        if 'emailcode' not in request.POST:

            verification_code = str(random.randint(100000, 999999))

            request.session['email_verification_code'] = verification_code
            request.session['email_verification_email'] = email
            request.session.modified = True

            send_mail(
                subject="Articlio Email Verification Code",
                message=f"Your verification code is: {verification_code}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )

            messages.success(request, "Verification code sent to your email")

            return render(request, 'home/forgetPassword.html', {
                "step": "verify","username":username,"email":email
            })
        entered_code = request.POST.get('emailcode')
        stored_code = request.session.get('email_verification_code')
        stored_email = request.session.get('email_verification_email')
        pass1=request.POST.get('pass1')
        pass2=request.POST.get('pass2')

        if not stored_code or stored_email != email:
            messages.error(request, "Verification session expired. Please try again.")
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
        request.session.modified = True

        user = User.objects.get(username=username,email=email)
        user.set_password(pass1)
        user.save()
        messages.success(request, "Password reset successfully")
        
        return redirect('handleLogin')