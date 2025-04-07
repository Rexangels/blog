# blog/urls.py
from django.urls import path
from . import views
# Import the new view if it's defined, e.g., CategoryListView
from .views import (
    AdvancedSearchView, NewsletterSignupView, SeriesDetailView,
    UserProfileUpdateView, PostListView, PostDetailView, PostCreateView,
    CommentCreateView, PostUpdateView, PostDeleteView, CategoryDetailView,
    TagDetailView, UserProfileView, BookmarkListView, CategoryListView # <-- Added CategoryListView here
)
# If CategoryListView is not defined yet, you'll need to create it in views.py

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
    path('series/<slug:slug>/follow/', views.toggle_follow_series, name='toggle_follow_series'),

    # Category and tag views
    path('category/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('tag/<slug:slug>/', views.TagDetailView.as_view(), name='tag_detail'),
    path('categories/', views.CategoryListView.as_view(), name='category_list'), # Maps URL to view


    # Search
    path('search/', views.AdvancedSearchView.as_view(), name='search_results'),

    # Newsletter
    path('newsletter/signup/', views.NewsletterSignupView.as_view(), name='newsletter_signup'),

    # Comments
    path('post/<slug:slug>/comment/', views.CommentCreateView.as_view(), name='add_comment'),
    path('comment/<int:pk>/like/', views.toggle_comment_like, name='toggle_comment_like'), # Moved comment like here

    # User profile
    path('profile/notifications/', views.update_notification_preferences, name='update_notification_preferences'),
    path('profile/edit/', UserProfileUpdateView.as_view(), name='profile_edit'),
    path('profile/<str:username>/', views.UserProfileView.as_view(), name='user_profile'),


    # Bookmarks
    path('bookmarks/', views.BookmarkListView.as_view(), name='bookmarks'),    
    path('post/<slug:slug>/bookmark/', views.toggle_bookmark, name='toggle_bookmark'),

    path('bookmarks/<int:pk>/update_notes/', views.update_bookmark_notes, name='update_bookmark_notes'),

    # Likes
    path('post/<slug:slug>/like/', views.toggle_like, name='post_like'),

    # RSS Feed (Assuming you have this view from the previous example)
    path('rss/', views.LatestPostsFeed(), name='rss_feed'), # Added RSS feed URL
]
