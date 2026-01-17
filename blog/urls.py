from django.urls import path
from blog import views

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
    path('<str:slug>',views.blogPost,name='blogPost'),
]