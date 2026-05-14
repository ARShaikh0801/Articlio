from django.urls import path
from blog import views, api_views

urlpatterns=[
    path('',views.blogHome,name='blogHome'),
    path('postComment',views.postComment,name="postComment"),
    path('filteredBlogs',views.filteredBlogs,name='filteredBlogs'),
    path('writeBlog',views.writeBlog,name='writeBlog'),
    path('myBlogs',views.myBlogs,name='myBlogs'),
    path('bookmarks',views.bookmarks,name='bookmarks'),
    path('toggle-like/',views.toggle_like,name='toggleLike'),
    path('toggle-bookmark/',views.toggle_bookmark,name='toggleBookmark'),
    path('verification',views.emailVerification,name='emailVerification'),
    path('edit/<str:slug>',views.editBlogPost,name='editBlogPost'),
    path('delete/<str:slug>',views.deleteBlogPost,name='deleteBlogPost'),
    
    path('api/posts/', api_views.api_posts, name='api_posts'),
    path('api/bookmarks/', api_views.api_bookmarks, name='api_bookmarks'),
    path('api/my-blogs/', api_views.api_my_blogs, name='api_my_blogs'),
    path('api/<str:slug>/state/', api_views.api_post_state, name='api_post_state'),
    path('api/<str:slug>/comments/', api_views.api_comments, name='api_comments'),
    
    path('<str:slug>',views.blogPost,name='blogPost'),
]