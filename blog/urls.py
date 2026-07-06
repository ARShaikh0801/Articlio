from django.urls import path
from blog import views, api_views

urlpatterns=[
    path('',views.blogHome,name='blogHome'),
    path('postComment',views.postComment,name="postComment"),
    path('filteredBlogs',views.filteredBlogs,name='filteredBlogs'),
    path('writeBlog',views.writeBlog,name='writeBlog'),
    path('myBlogs',views.myBlogs,name='myBlogs'),
    path('bookmarks',views.bookmarks,name='bookmarks'),
    path('history',views.history,name='history'),
    path('toggle-like/',views.toggle_like,name='toggleLike'),
    path('toggle-comment-like/',views.toggle_comment_like,name='toggleCommentLike'),
    path('toggle-bookmark/',views.toggle_bookmark,name='toggleBookmark'),
    path('verification',views.emailVerification,name='emailVerification'),
    path('edit/<str:slug>',views.editBlogPost,name='editBlogPost'),
    path('delete/<str:slug>',views.deleteBlogPost,name='deleteBlogPost'),
    
    path('api/posts/', api_views.api_posts, name='api_posts'),
    path('api/bookmarks/', api_views.api_bookmarks, name='api_bookmarks'),
    path('api/my-blogs/', api_views.api_my_blogs, name='api_my_blogs'),
    path('api/history/', api_views.api_history, name='api_history'),
    path('api/history/track/', api_views.api_track_history, name='api_track_history'),
    path('api/<str:slug>/state/', api_views.api_post_state, name='api_post_state'),
    path('api/<str:slug>/comments/', api_views.api_comments, name='api_comments'),
    
    path('api/<str:slug>/highlights/', api_views.api_highlights, name='api_highlights'),
    path('api/highlights/create/', api_views.api_create_highlight, name='api_create_highlight'),
    path('api/highlights/<int:id>/update/', api_views.api_update_highlight, name='api_update_highlight'),
    path('api/highlights/<int:id>/delete/', api_views.api_delete_highlight, name='api_delete_highlight'),
    
    path('<str:slug>',views.blogPost,name='blogPost'),
]