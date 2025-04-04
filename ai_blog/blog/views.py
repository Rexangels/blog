# blog/views.py
import logging
from django.shortcuts import redirect, reverse, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Post, Category, Tag, Newsletter, AdSpace, Comment, PageVisit
from .forms import PostForm, NewsletterForm, CommentForm
from django.views.generic import ( 
    ListView, DetailView, CreateView, UpdateView, DeleteView,
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q, Count, Max
from django.urls import reverse_lazy, reverse
from django.views.generic import DetailView, ListView
from django.contrib.auth.models import User
from .models import Series
from .models import UserProfile, Bookmark, PostLike
from .forms import UserProfileForm
from django.http import JsonResponse

logger = logging.getLogger(__name__)

class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        # Filter for public posts and annotate with comment count
        return Post.objects.filter(visibility='public', status='published').annotate(
            comment_count=Count('comments')
        ).order_by('-created_at')

    def _add_categories_tags_top_posts(self, context):
        context['categories'] = Category.objects.all()
        context['tags'] = Tag.objects.all()
        context['top_posts'] = Post.objects.filter(
            visibility='public', status='published'
        ).order_by('-view_count')[:5]    
    



    
    def _add_newsletter_form(self, context):
        context['newsletter_form'] = NewsletterForm()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self._add_categories_tags_top_posts(context)
        
        return context

class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'

    def _add_related_posts(self, context):
        post = self.object
        context['related_posts'] = Post.objects.filter(
            categories__in=post.categories.all(),
            visibility='public',
            status='published'
        ).exclude(pk=post.pk).distinct()[:3]

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
        post.save()
        
        # Track page visit if needed
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
        return context

class PostCreateView(LoginRequiredMixin, CreateView):
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
                Q(content__icontains=query)
            )
        
        if category:
            queryset = queryset.filter(categories__slug=category)
        
        if tags:
            queryset = queryset.filter(tags__slug__in=tags)
        
        return queryset.annotate(comment_count=Count('comments')).order_by('-created_at')
    
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
        comment.likes = max(0, comment.likes - 1)
    else:
        comment.likes += 1
    
    comment.save()
    
    # If it's an AJAX request, return JSON response
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'like_count': comment.likes,
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