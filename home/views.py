from django.shortcuts import render,redirect
from django.http import JsonResponse
import json
from django.contrib import messages
from home.models import Contact
from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib.auth import authenticate,login,logout
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import random
import base64
import hashlib
import hmac
import uuid
import logging

logger = logging.getLogger(__name__)

def home(request):
    return render(request,'home/home.html')

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


# ── Facebook Data Deletion Callback ──────────────────────────────────────────

def _parse_signed_request(signed_request, secret):
    """
    Decode and verify a Facebook signed_request.
    Returns the decoded payload dict, or None if verification fails.
    """
    try:
        encoded_sig, payload = signed_request.split('.', 1)

        # Decode the signature
        sig = base64.urlsafe_b64decode(encoded_sig + '==')

        # Decode the payload
        data = json.loads(base64.urlsafe_b64decode(payload + '=='))

        # Verify HMAC-SHA256 signature
        expected_sig = hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256,
        ).digest()

        if not hmac.compare_digest(sig, expected_sig):
            logger.warning('Facebook signed_request signature mismatch')
            return None

        return data
    except Exception as e:
        logger.error('Failed to parse Facebook signed_request: %s', e)
        return None


@csrf_exempt
@require_POST
def facebook_deletion_callback(request):
    """
    Facebook Data Deletion Callback endpoint.

    When a user removes the Articlio app from their Facebook account,
    Facebook sends a POST request here with a `signed_request` parameter.
    We verify the signature, identify the user, delete their Facebook-linked
    data, and return a JSON response with a confirmation code and status URL.
    """
    signed_request = request.POST.get('signed_request')
    if not signed_request:
        return JsonResponse({'error': 'Missing signed_request'}, status=400)

    # Get the Facebook app secret
    fb_secret = settings.SOCIALACCOUNT_PROVIDERS.get('facebook', {}).get(
        'APP', {}
    ).get('secret', '')

    if not fb_secret:
        logger.error('Facebook app secret not configured')
        return JsonResponse({'error': 'Server configuration error'}, status=500)

    data = _parse_signed_request(signed_request, fb_secret)
    if data is None:
        return JsonResponse({'error': 'Invalid signed_request'}, status=403)

    fb_user_id = data.get('user_id')
    if not fb_user_id:
        return JsonResponse({'error': 'No user_id in signed_request'}, status=400)

    # Generate a unique confirmation code for this deletion request
    confirmation_code = uuid.uuid4().hex[:12]

    # Delete the user's Facebook social account link and related data
    try:
        from allauth.socialaccount.models import SocialAccount, SocialToken

        social_accounts = SocialAccount.objects.filter(
            provider='facebook', uid=fb_user_id
        )

        for sa in social_accounts:
            user = sa.user

            # Delete social tokens for this account
            SocialToken.objects.filter(account=sa).delete()

            # Delete the social account link itself
            sa.delete()

            logger.info(
                'Deleted Facebook social account for user %s (fb_uid=%s, code=%s)',
                user.pk, fb_user_id, confirmation_code,
            )
    except Exception as e:
        logger.error('Error during Facebook data deletion: %s', e)
        # Still return success to Facebook — we'll handle cleanup manually
        # if needed, and Facebook expects a 200 response.

    # Build the status-check URL
    host = request.get_host()
    scheme = 'https' if request.is_secure() else 'http'
    status_url = f'{scheme}://{host}/facebook/deletion-status/?code={confirmation_code}'

    return JsonResponse({
        'url': status_url,
        'confirmation_code': confirmation_code,
    })


def facebook_deletion_status(request):
    """
    Simple status page for Facebook data deletion confirmation.
    Facebook shows this URL to users who want to check deletion status.
    """
    code = request.GET.get('code', '')
    return render(request, 'home/facebook_deletion_status.html', {
        'confirmation_code': code,
    })