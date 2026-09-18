from django.urls import path
from home import views, api_views

urlpatterns=[
    path('',views.home,name='home'),
    path('contact',views.contact,name='contact'),
    path('about',views.about,name='blog'),
    path('search',views.search,name='search'),
    path('signup',views.handleSignup,name='handleSignup'),
    path('login',views.handleLogin,name='handleLogin'),
    path('logout',views.handleLogout,name='handleLogout'),
    path('terms',views.terms,name='terms'),
    path('privacy',views.privacy,name='privacy'),
    path('resetpass',views.resetPassword,name='resetPassword'),
    path('update-theme', views.update_theme_preference, name='update_theme_preference'),
    path('complete-profile', views.complete_profile, name='complete_profile'),
    
    path('profile/', views.profile, name='profile'),
    path('profile/toggle-follow/', views.toggle_follow, name='toggle_follow'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('profile/<str:username>/', views.profile, name='public_profile'),
    path('api/profile/articles/<str:username>/', views.api_author_posts, name='api_author_posts'),
    path('api/profile/followers/<str:username>/', views.api_profile_followers, name='api_profile_followers'),
    path('api/profile/following/<str:username>/', views.api_profile_following, name='api_profile_following'),

    path('api/home/posts/', api_views.api_home_posts, name='api_home_posts'),
    path('api/search/', api_views.api_search, name='api_search'),
    path('api/check-username/', views.check_username_availability, name='check_username_availability'),
    path('api/suggested-authors/', views.api_suggested_authors, name='api_suggested_authors'),

    path('onboarding/', views.onboarding, name='onboarding'),
]