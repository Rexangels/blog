# blog/urls.py
from django.urls import path
from .views import AdvancedSearchView
from .views import (
    PostListView, 
    PostDetailView, 
    PostCreateView, 
    CommentCreateView
)

app_name = 'blog'

urlpatterns = [
    path('', PostListView.as_view(), name='home'),
    path('post/<slug:slug>/', PostDetailView.as_view(), name='post_detail'),
    path('post/new/', PostCreateView.as_view(), name='post_create'),
    path('post/<slug:slug>/comment/', CommentCreateView.as_view(), name='add_comment'),
]


urlpatterns += [
    path('search/', AdvancedSearchView.as_view(), name='search'),
]