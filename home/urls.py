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

    path('api/home/posts/', api_views.api_home_posts, name='api_home_posts'),
    path('api/search/', api_views.api_search, name='api_search'),
    path('api/check-username/', views.check_username_availability, name='check_username_availability'),
]