# blog/views.py
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Post, Category, Tag, Newsletter, Comment, PageVisit, CommentLike, Notification, UserProfile, UserNotificationSettings
from .forms import PostForm, CommentForm, UserNotificationSettingsForm, NewsletterForm
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.contrib.syndication.views import Feed
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q, Count, Max, F
from django.urls import reverse_lazy, reverse
from django.views.generic import DetailView, ListView
from django.contrib.auth.models import User, Group
from .models import Series
from .models import SeriesFollower, UserNotificationSettings
from .models import Bookmark, PostLike
from .forms import UserProfileForm
from django.http import JsonResponse

logger = logging.getLogger(__name__)

class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        # Optimized: Added select_related and prefetch_related to reduce DB queries
        return Post.objects.filter(visibility='public', status='published').annotate(
            comment_count=Count('comments')
        ).select_related('author').prefetch_related('categories', 'tags').order_by('-created_at')

    def _add_categories_tags_top_posts(self, context):
        # Cache these queries with timeouts
        context['categories'] = Category.objects.all()
        context['tags'] = Tag.objects.all()
        context['top_posts'] = Post.objects.filter(
            visibility='public', status='published'
        ).select_related('author').order_by('-view_count')[:5]    
    
    def _add_newsletter_form(self, context):
        context['newsletter_form'] = NewsletterForm()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self._add_categories_tags_top_posts(context)

        # Optimize likes check with a single query instead of one per post
        if self.request.user.is_authenticated:
            liked_posts = set(PostLike.objects.filter(
                user=self.request.user, 
                post__in=context['posts']
            ).values_list('post_id', flat=True))
            
            for post in context['posts']:
                post.is_liked = post.id in liked_posts
        else:
            for post in context['posts']:
                post.is_liked = False
        
        return context

class LatestPostsFeed(Feed):
    title = "My blog"
    link = "/blog/"
    description = "Latest posts from my blog"

    def items(self):
        return Post.objects.filter(status='published', visibility='public').order_by('-pub_date')[:5]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.content[:200] + '...'        
                
                
    def item_link(self, item):
        return reverse("blog:post_detail", args=[item.slug])

    def item_pubdate(self, item):
        return item.pub_date
        return context

class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'

    def get_queryset(self):
        # Add select_related and prefetch_related to reduce database queries
        return Post.objects.select_related('author').prefetch_related(
            'categories', 'tags', 'comments__user'
        )

    def _add_related_posts(self, context):
        """
        Find related posts based on shared categories and tags.
        Posts with more shared categories and tags are ranked higher.
        """
        post = self.object
        
        # Get the current post's categories and tags
        post_categories = post.categories.all()
        post_tags = post.tags.all()
        
        # Get all published posts except the current one
        candidate_posts = Post.objects.filter(
            visibility='public',
            status='published'
        ).exclude(pk=post.pk)
        
        # If post has categories, prioritize posts from same categories
        if post_categories:
            # Annotate posts with a score based on shared categories
            candidate_posts = candidate_posts.annotate(
                shared_categories=Count('categories', filter=Q(categories__in=post_categories))
            )
        else:
            # If no categories, set shared_categories to 0
            candidate_posts = candidate_posts.annotate(
                shared_categories=Count('categories', filter=Q(categories__in=[]))
            )
        
        # If post has tags, prioritize posts with shared tags
        if post_tags:
            # Annotate posts with a score based on shared tags
            candidate_posts = candidate_posts.annotate(
                shared_tags=Count('tags', filter=Q(tags__in=post_tags))
            )
        else:
            # If no tags, set shared_tags to 0
            candidate_posts = candidate_posts.annotate(
                shared_tags=Count('tags', filter=Q(tags__in=[]))
            )
        
        # Calculate total relevance score (weighted: categories matter more than tags)
        candidate_posts = candidate_posts.annotate(
            relevance_score=(F('shared_categories') * 2) + F('shared_tags')
        )
        
        # Order by relevance score (highest first), then by published date (newest first)
        related_posts = candidate_posts.order_by('-relevance_score', '-published_date')
        
        # Limit to 3 related posts with at least one shared category or tag
        context['related_posts'] = related_posts.filter(
            Q(shared_categories__gt=0) | Q(shared_tags__gt=0)
        ).select_related('author').prefetch_related('categories', 'tags')[:3]
        
        # If we don't have 3 related posts yet, add some recent posts
        if context['related_posts'].count() < 3:
            remaining_count = 3 - context['related_posts'].count()
            recent_posts = candidate_posts.exclude(
                pk__in=[p.pk for p in context['related_posts']]
            ).order_by('-published_date')[:remaining_count]
            
            # Combine the two querysets
            context['related_posts'] = list(context['related_posts']) + list(recent_posts)

    def get_object(self, queryset=None):
        if self.kwargs.get('slug') == 'new':
            return None
        return super().get_object(queryset=queryset)
    
    def get(self, request, *args, **kwargs):
        if self.kwargs.get('slug') == 'new':
            return redirect('blog:home')
        
        # Increment view count
        post = self.get_object()
        post.view_count += 1
        post.save(update_fields=['view_count'])  # Only update the view_count field

        # Track page visit if needed - but do it asynchronously or in a background task if possible
        if request.user.is_authenticated:
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            referrer = request.META.get('HTTP_REFERER', '')
            PageVisit.objects.create(
                page_url=request.path,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=user_agent,
                referrer=referrer
            )

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self._add_related_posts(context)
        context['comment_form'] = CommentForm()
        
        # Optimize comment likes check with a single query instead of one per comment
        comments = context['post'].comments.all()
        
        if self.request.user.is_authenticated and comments:
            liked_comments = set(CommentLike.objects.filter(
                user=self.request.user, 
                comment__in=comments
            ).values_list('comment_id', flat=True))
            
            for comment in comments:
                comment.is_liked = comment.id in liked_comments
        else:
            for comment in comments:
                comment.is_liked = False

        return context

class PostCreateView(LoginRequiredMixin,CreateView):
    form_class = PostForm
    template_name = 'blog/post_form.html'
    
    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user
        
        # Check if publish button was clicked
        if 'publish' in self.request.POST:
            post.status = 'published'
            post.visibility = 'public'            
            post.published_date = timezone.now()            
        else:
            post.status = 'draft'
            post.visibility = 'private'
        
        post.save()

        if not post.slug:            
            post.slug = "-".join(post.title.lower().split())
            post.save()
        form.save_m2m()  # Save many-to-many fields

        # Create notifications if the post is published.
        if post.status == 'published':
            if post.series:
                # If the post belongs to a series, notify only the followers of that series.
                followers = SeriesFollower.objects.filter(series=post.series)
                for follower in followers:
                    # Skip creating notification for the author
                    if follower.user == post.author:
                         continue
                    # Check if the user wants series notifications
                    user_settings = follower.user.notification_settings
                    if user_settings.receive_series_notifications:
                        Notification.objects.create(
                            user=follower.user,
                            post=post,
                            message=f'New post "{post.title}" in the series "{post.series.title}".'
                    )
            else:
                # If the post does not belong to a series, notify all users (existing logic).
                all_users = User.objects.all()
                for user in all_users:
                    # Skip creating notification for the author
                    if user == post.author:
                        continue

                    user_settings = user.notification_settings
                    # Check if the user wants post notifications
                    if user_settings.receive_post_notifications:
                        Notification.objects.create(
                            user=user,
                            post=post,
                            message=f'New post: {post.title}'
                        )


        
        messages.success(self.request, 'Post created successfully!')
        
        # Debugging: Print slug and redirect URL
        logger.debug(f"Post slug: {post.slug}")
        redirect_url = reverse('blog:post_detail', kwargs={'slug': post.slug})
        logger.debug(f"Redirect URL: {redirect_url}")
        return redirect('blog:post_detail', slug=post.slug)

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    form_class = PostForm
    template_name = 'blog/post_form.html'
    
    def form_valid(self, form):
        post = form.save(commit=False)
        
        # Check if publish button was clicked
        if 'publish' in self.request.POST and post.status == 'draft':
            post.status = 'published'
            post.visibility = 'public'
            post.published_date = timezone.now()
        
        post.save()
        form.save_m2m()
        
        messages.success(self.request, 'Post updated successfully!')
        return redirect('blog:post_detail', slug=post.slug)
    
    def test_func(self):
        # Check if the current user is the author of the post
        post = self.get_object()
        return self.request.user == post.author

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    success_url = reverse_lazy('blog:home')
    template_name = 'blog/post_confirm_delete.html'
    
    def test_func(self):
        # Check if the current user is the author of the post
        post = self.get_object()
        return self.request.user == post.author

class CategoryDetailView(ListView):
    model = Post
    template_name = 'blog/category_detail.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        category_slug = self.kwargs['slug']
        return Post.objects.filter(
            categories__slug=category_slug,
            visibility='public',
            status='published'
        ).annotate(
            comment_count=Count('comments')
        ).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = self.kwargs['slug']
        context['category'] = Category.objects.get(slug=category_slug)
        context['categories'] = Category.objects.all()
        return context

class TagDetailView(ListView):
    model = Post
    template_name = 'blog/tag_detail.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        tag_slug = self.kwargs['slug']
        return Post.objects.filter(
            tags__slug=tag_slug,
            visibility='public',
            status='published'
        ).annotate(
            comment_count=Count('comments')
        ).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag_slug = self.kwargs['slug']
        context['tag'] = Tag.objects.get(slug=tag_slug)
        context['categories'] = Category.objects.all()
    

    def get_queryset(self):
        tag_slug = self.kwargs['slug']
        return Post.objects.filter(

            tags__slug=tag_slug,
            visibility='public',
            status='published'
        ).annotate(
            comment_count=Count("comments")
        ).order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class SeriesDetailView(ListView):
    model = Post
    template_name = "blog/series_detail.html"
    context_object_name = "posts"
    paginate_by = 10

    def get_queryset(self):
        series_slug = self.kwargs["slug"]
        return Post.objects.filter(series__slug=series_slug, visibility="public", status="published").order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        series_slug = self.kwargs["slug"]
        context["series"] = Series.objects.get(slug=series_slug)
        
        # Check if the user is following the series
        if self.request.user.is_authenticated:
            context["is_following"] = SeriesFollower.objects.filter(user=self.request.user, series=context["series"]).exists()
        else:
            context["is_following"] = False

        return context

class AdvancedSearchView(ListView):
    model = Post
    template_name = 'blog/search_results.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get('q')
        category = self.request.GET.get('category')
        tags = self.request.GET.getlist('tags')
        
        queryset = Post.objects.filter(visibility='public', status='published')
        
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | 
                Q(content__icontains=query) # Fixed missing '='
            )
        
        if category:
            queryset = queryset.filter(categories__slug=category)
        
        if tags:
            queryset = queryset.filter(tags__slug__in=tags)
        
        return queryset.annotate(comment_count=Count('comments')).select_related('author').prefetch_related('categories', 'tags').order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['categories'] = Category.objects.all()
        context['tags'] = Tag.objects.all()
        context['selected_category'] = self.request.GET.get('category')
        context['selected_tags'] = self.request.GET.getlist('tags')
        return context

class NewsletterSignupView(CreateView):
    model = Newsletter
    form_class = NewsletterForm
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Thank you for subscribing to our newsletter!')
        # Redirect back to the page they were on
        return HttpResponseRedirect(self.request.META.get('HTTP_REFERER', '/'))
    
    def form_invalid(self, form):
        # If email already exists, show friendly message
        if 'email' in form.errors and 'This email is already subscribed' in str(form.errors['email']):
            messages.info(self.request, 'This email is already subscribed to our newsletter.')
        else:
            messages.error(self.request, 'There was an error with your submission. Please try again.')
        # Redirect back to the page they were on
        return HttpResponseRedirect(self.request.META.get('HTTP_REFERER', '/'))
    
    
class CommentCreateView(CreateView):
    model = Comment
    form_class = CommentForm
    
    def form_valid(self, form):
        form.instance.post = Post.objects.get(slug=self.kwargs['slug'])
        response = super().form_valid(form)
        messages.success(self.request, 'Your comment has been added successfully!')
        return response
    
    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'slug': self.kwargs['slug']})

class UserProfileView(DetailView):
    model = User
    template_name = 'blog/user_profile.html'
    context_object_name = 'profile_user'
    
    def get_object(self):
        return get_object_or_404(User, username=self.kwargs['username'])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        
        # Get user's posts
        context['user_posts'] = Post.objects.filter(
            author=user, 
            status='published',
            visibility='public'
        ).order_by('-published_date')
        
        # Get user's recent comments
        context['user_comments'] = Comment.objects.filter(
            user=user,
            status='approved'
        ).order_by('-created_at')[:10]
        
        context['categories'] = Category.objects.all()
        return context


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'blog/user_profile_form.html'
    
    def get_object(self):
        return self.request.user.profile
    
    def form_valid(self, form):
        super().form_valid(form)
        messages.success(self.request, 'Profile updated successfully!')
        return redirect(reverse('blog:user_profile', kwargs={'username': self.request.user.username}))

class BookmarkListView(LoginRequiredMixin, ListView):
    model = Bookmark
    template_name = 'blog/bookmarks.html'
    context_object_name = 'bookmarks'
    paginate_by = 10
    
    def get_queryset(self):
        return Bookmark.objects.filter(user=self.request.user).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

# Add a view for toggling bookmarks
@login_required
def toggle_bookmark(request, slug):
    post = get_object_or_404(Post, slug=slug)
    bookmark, created = Bookmark.objects.get_or_create(user=request.user, post=post)
    
    if not created:
        # If bookmark already existed, remove it
        bookmark.delete()
        post.bookmark_count = max(0, post.bookmark_count - 1)
        messages.success(request, f'Removed {post.title} from your bookmarks.')
    else:
        post.bookmark_count += 1
        messages.success(request, f'Added {post.title} to your bookmarks.')
    
    post.save()
    
    # Redirect back to the referring page
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', post.get_absolute_url()))

# Add a view for toggling likes
@login_required
def toggle_like(request, slug):
    post = get_object_or_404(Post, slug=slug)
    like, created = PostLike.objects.get_or_create(user=request.user, post=post)
    
    if not created:
        # If like already existed, remove it
        like.delete()
        post.like_count = max(0, post.like_count - 1)
    else:
        post.like_count += 1
    
    post.save()
    
    # If it's an AJAX request, return JSON response
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'like_count': post.like_count,
            'liked': created
        })
    
    # Redirect back to the referring page
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', post.get_absolute_url()))


@login_required
def toggle_comment_like(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    like, created = CommentLike.objects.get_or_create(user=request.user, comment=comment)
    
    if not created:
        # If like already existed, remove it
        like.delete()
        comment.like_count = max(0, comment.like_count - 1)
    else:
        comment.like_count += 1
    
    comment.save()
    
    # If it's an AJAX request, return JSON response
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'like_count': comment.like_count,
            'liked': created
        })
    
    # Redirect back to the referring page
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', comment.post.get_absolute_url()))


@login_required
def update_bookmark_notes(request, pk):
    bookmark = get_object_or_404(Bookmark, pk=pk, user=request.user)
    
    if request.method == 'POST':
        notes = request.POST.get('notes', '')
        bookmark.notes = notes
        bookmark.save()
        messages.success(request, "Notes updated successfully.")
    
    # Redirect back to bookmarks page
    return redirect('blog:bookmarks')

@login_required
def toggle_follow_series(request, slug):
    series = get_object_or_404(Series, slug=slug)
    follower = SeriesFollower.objects.filter(user=request.user, series=series).first()
    if follower:
        follower.delete()
        messages.success(request, f'You have unfollowed {series.title}.')
    else:
        SeriesFollower.objects.create(user=request.user, series=series)
        messages.success(request, f'You are now following {series.title}.')
    return redirect('blog:series_detail', slug=slug)






@login_required
def update_notification_preferences(request):
    settings, created = UserNotificationSettings.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserNotificationSettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, 'Notification preferences updated successfully.')
            return redirect('blog:user_profile', username=request.user.username)
    else:
        form = UserNotificationSettingsForm(instance=settings)
    return render(request, 'blog/notification_preferences_form.html', {'form': form})
import logging

class CategoryListView(ListView):
    model = Category
    template_name = 'blog/category_list.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        return Category.objects.all().annotate(
            post_count=Count('post', filter=Q(post__visibility='public', post__status='published'))
        ).order_by('name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

def search_autocomplete(request):
    """API endpoint that returns search suggestions as user types."""
    query = request.GET.get('q', '').strip()
    results = []
    
    if query and len(query) >= 2:  # Only process queries with at least 2 characters
        # Search in post titles with priority
        title_results = Post.objects.filter(
            title__icontains=query,
            visibility='public',
            status='published'
        ).values('title', 'slug')[:5]
        
        # Add post titles to results
        for post in title_results:
            results.append({
                'title': post['title'],
                'url': reverse('blog:post_detail', kwargs={'slug': post['slug']}),
                'type': 'post'
            })
            
        # If we have fewer than 5 results, also search in categories
        if len(results) < 5:
            remaining = 5 - len(results)
            category_results = Category.objects.filter(
                name__icontains=query
            ).values('name', 'slug')[:remaining]
            
            # Add categories to results
            for category in category_results:
                results.append({
                    'title': category['name'],
                    'url': reverse('blog:category_detail', kwargs={'slug': category['slug']}),
                    'type': 'category'
                })
        
        # If we still have fewer than 5 results, also search in tags
        if len(results) < 5:
            remaining = 5 - len(results)
            tag_results = Tag.objects.filter(
                name__icontains=query
            ).values('name', 'slug')[:remaining]
            
            # Add tags to results
            for tag in tag_results:
                results.append({
                    'title': tag['name'],
                    'url': reverse('blog:tag_detail', kwargs={'slug': tag['slug']}),
                    'type': 'tag'
                })
    
    return JsonResponse({'results': results})