import math
from django.core.cache import cache
from home.models import CustomUser

class BloomFilter:
    """
    A simple custom Bloom Filter implementation.
    """
    def __init__(self, size=10000, num_hashes=3):
        """
        size: The number of bits in the array. 
              Larger size = less false positives but uses more memory.
        num_hashes: The number of hash functions to use.
        """
        self.size = size
        self.num_hashes = num_hashes
        
        # In Python, we can just use a list of booleans or an integer as a bit array.
        # A list of booleans is very easy to understand and work with.
        self.bit_array = [False] * size
        
        # We will use simple prime numbers as "seeds" for our custom hash functions.
        # This gives us different hash results for the same string.
        self.seeds = [31, 37, 41, 43, 47, 53, 59, 61, 67, 71][:num_hashes]

    def _custom_hash(self, item, seed):
        """
        Our very own simple hash function!
        It converts characters to numbers and multiplies them by the seed.
        """
        hash_value = 0
        for char in str(item):
            # ord(char) gets the numerical ASCII value of the character (e.g., 'A' -> 65)
            # We multiply by the seed and add it to the running total.
            hash_value = (hash_value * seed) + ord(char)
            
        # The modulo operator (%) ensures the hash value fits inside our bit array size.
        # E.g., if hash is 10005 and size is 10000, it wraps around to index 5.
        return hash_value % self.size

    def add(self, item):
        """
        Adds an item (like a username) to the Bloom Filter.
        """
        for seed in self.seeds:
            index = self._custom_hash(item, seed)
            # Set the bit at this index to True (1)
            self.bit_array[index] = True

    def check(self, item):
        """
        Checks if an item is probably in the Bloom Filter.
        Returns True if it is PROBABLY TAKEN.
        Returns False if it is DEFINITELY AVAILABLE.
        """
        for seed in self.seeds:
            index = self._custom_hash(item, seed)
            # If ANY bit is False, the item was definitely never added.
            if not self.bit_array[index]:
                return False
                
        # If all bits were True, it MIGHT be taken.
        return True

def get_username_bloom_filter():
    """
    Retrieves the Bloom Filter from Django's cache.
    If it doesn't exist (e.g., server restarted or cache cleared),
    it rebuilds it by fetching all usernames from the database.
    """
    # Try to get the filter from the cache
    bf = cache.get('username_bloom_filter')
    
    if bf is None:
        # If not found, create a new one!
        # size=100000 gives us plenty of room for users with very few false positives.
        bf = BloomFilter(size=100000, num_hashes=3)
        
        # Fetch all existing usernames from the database
        # We use .values_list for performance, so we don't load full user objects.
        usernames = CustomUser.objects.values_list('username', flat=True)
        
        # Add every single username to our Bloom Filter
        for username in usernames:
            bf.add(username.lower()) # Lowercase to make it case-insensitive
            
        # Save our fully loaded Bloom Filter into the cache!
        # Timeout=None means it stays in cache indefinitely (until memory is full or server restarts)
        cache.set('username_bloom_filter', bf, timeout=None)
        
    return bf

# Theme Color Palettes (mapped to HEX/RGBA for email client compatibility)
THEME_COLORS = {
    'ocean': {
        'primary': '#3a7cc0',
        'darkest': '#172a3c',
        'dark': '#24415e',
        'medium': '#5591cd',
        'light': '#e3ebf2',
        'lightest': '#f4f6f9',
        'faded_rgba': 'rgba(58, 124, 192, 0.1)'
    },
    'emerald': {
        'primary': '#3da88a',
        'darkest': '#1b4337',
        'dark': '#296a57',
        'medium': '#53b89b',
        'light': '#e1f3ed',
        'lightest': '#f4faf7',
        'faded_rgba': 'rgba(61, 168, 138, 0.1)'
    },
    'slate': {
        'primary': '#575e6d',
        'darkest': '#282b32',
        'dark': '#3e434e',
        'medium': '#71798a',
        'light': '#e8e9eb',
        'lightest': '#f5f5f6',
        'faded_rgba': 'rgba(87, 94, 109, 0.1)'
    },
    'crimson': {
        'primary': '#b04050',
        'darkest': '#44141a',
        'dark': '#6c202a',
        'medium': '#c15f6e',
        'light': '#f7e8ea',
        'lightest': '#fbf5f6',
        'faded_rgba': 'rgba(176, 64, 80, 0.1)'
    },
    'violet': {
        'primary': '#7a50b0',
        'darkest': '#2c1c3f',
        'dark': '#452c63',
        'medium': '#946ec3',
        'light': '#ede6f5',
        'lightest': '#f8f6fb',
        'faded_rgba': 'rgba(122, 80, 176, 0.1)'
    }
}

from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings

def send_verification_email(user, code, purpose, request=None):
    """
    Sends a beautiful HTML verification email tailored to the user's theme preference.
    purpose can be 'reset_password' or 'verify_email'.
    """
    theme = getattr(user, 'theme_preference', 'ocean')
    colors = THEME_COLORS.get(theme, THEME_COLORS['ocean'])
    
    site_url = request.build_absolute_uri('/') if request else 'http://localhost:8000/'
    
    if purpose == 'reset_password':
        subject = "Reset Your Articlio Password"
        title = "Reset Password Request"
        description = "We received a request to reset your password. Use the verification code below to complete the reset process."
    else:
        subject = "Verify Your Articlio Email"
        title = "Email Verification"
        description = "Thank you for joining Articlio! Please verify your email address to activate your account and start posting blogs."
        
    context = {
        'username': user.username,
        'code': code,
        'purpose': purpose,
        'title': title,
        'description': description,
        'colors': colors,
        'site_url': site_url,
    }
    
    html_content = render_to_string('emails/verification_code.html', context)
    text_content = f"Hi {user.username},\n\n{description}\n\nYour 6-digit verification code is: {code}\n\nThis code will expire in 30 minutes.\n\nBest,\nThe Articlio Team"
    
    send_mail(
        subject=subject,
        message=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_content,
        fail_silently=False,
    )

