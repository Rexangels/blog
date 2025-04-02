# blog/urls.py
from django.urls import path
from . import views
from .views import AdvancedSearchView, NewsletterSignupView, SeriesDetailView
from .views import (
    PostListView, 
    PostDetailView, 
    PostCreateView, 
    CommentCreateView,
    PostUpdateView, PostDeleteView
)

app_name = 'blog'

urlpatterns = [
    # Post views
    path('', views.PostListView.as_view(), name='home'),
    path('post/<slug:slug>/', views.PostDetailView.as_view(), name='post_detail'),
    path('post/new/', views.PostCreateView.as_view(), name='post_create'),
    path('post/<slug:slug>/edit/', views.PostUpdateView.as_view(), name='post_edit'),
    path('post/<slug:slug>/delete/', views.PostDeleteView.as_view(), name='post_delete'),
    
    # Series views
    path('series/<slug:slug>/', SeriesDetailView.as_view(), name='series_detail'),

    # Category and tag views
    path('category/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('tag/<slug:slug>/', views.TagDetailView.as_view(), name='tag_detail'),
    
    # Search
    path('search/', views.AdvancedSearchView.as_view(), name='search_results'),
    
    # Newsletter
    path('newsletter/signup/', views.NewsletterSignupView.as_view(), name='newsletter_signup'),
    
    # Comments
    path('post/<slug:slug>/comment/', views.CommentCreateView.as_view(), name='add_comment'),
    # User profile
    path('profile/<str:username>/', views.UserProfileView.as_view(), name='user_profile'),
    
    # Bookmarks
    path('bookmarks/', views.BookmarkListView.as_view(), name='bookmarks'),
    path('post/<slug:slug>/bookmark/', views.toggle_bookmark, name='post_bookmark'),
    
    # Likes
    path('post/<slug:slug>/like/', views.toggle_like, name='post_like'),
    path('bookmarks/<int:pk>/update_notes/', views.update_bookmark_notes, name='update_bookmark_notes'),
]