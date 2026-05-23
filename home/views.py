from django.shortcuts import render,redirect
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
                user.save()
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