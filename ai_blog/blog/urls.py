# blog/urls.py
from django.urls import path
from . import views
from .views import AdvancedSearchView, NewsletterSignupView
from .views import (
    PostListView, 
    PostDetailView, 
    PostCreateView, 
    CommentCreateView,
)

app_name = 'blog'

urlpatterns = [
    # Post views
    path('', views.PostListView.as_view(), name='home'),
    path('post/<slug:slug>/', views.PostDetailView.as_view(), name='post_detail'),
    path('post/new/', views.PostCreateView.as_view(), name='post_create'),
    path('post/<slug:slug>/edit/', views.PostUpdateView.as_view(), name='post_edit'),
    path('post/<slug:slug>/delete/', views.PostDeleteView.as_view(), name='post_delete'),
    
    # Category and tag views
    path('category/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('tag/<slug:slug>/', views.TagDetailView.as_view(), name='tag_detail'),
    
    # Search
    path('search/', views.AdvancedSearchView.as_view(), name='search'),
    
    # Newsletter
    path('newsletter/signup/', views.NewsletterSignupView.as_view(), name='newsletter_signup'),
    
    # Comments
    path('post/<slug:slug>/comment/', views.CommentCreateView.as_view(), name='add_comment'),
]