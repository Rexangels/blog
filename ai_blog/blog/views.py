# blog/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Post, Category, Tag, Newsletter, AdSpace, Comment, PageVisit
from .forms import PostForm, NewsletterForm, CommentForm
from django.views.generic import ( 
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q, Count
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['tags'] = Tag.objects.all()
        context['top_posts'] = Post.objects.filter(visibility='public', status='published').order_by('-view_count')[:5]
        context['ads'] = AdSpace.objects.filter(is_active=True)
        context['newsletter_form'] = NewsletterForm()
        return context

class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'

    def get(self, request, *args, **kwargs):
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
        post = self.object
        # Get related posts based on categories
        related_posts = Post.objects.filter(
            categories__in=post.categories.all(),
            visibility='public',
            status='published'
        ).exclude(pk=post.pk).distinct()[:3]
        
        context['related_posts'] = related_posts
        context['comment_form'] = CommentForm()
        context['ads'] = AdSpace.objects.filter(is_active=True)
        context['newsletter_form'] = NewsletterForm()
        return context

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
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
        form.save_m2m()  # Save many-to-many fields
        
        messages.success(self.request, 'Post created successfully!')
        return redirect('blog:post_detail', slug=post.slug)

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
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
    model = Post
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
        context['ads'] = AdSpace.objects.filter(is_active=True)
        context['newsletter_form'] = NewsletterForm()
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
        context['ads'] = AdSpace.objects.filter(is_active=True)
        context['newsletter_form'] = NewsletterForm()
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
    
    def get_success_url(self):
        return reverse_lazy('blog:home')

class CommentCreateView(CreateView):
    model = Comment
    form_class = CommentForm
    
    def form_valid(self, form):
        form.instance.post = Post.objects.get(slug=self.kwargs['slug'])
        response = super().form_valid(form)
        messages.success(self.request, 'Your comment has been added successfully!')
        return response
    
    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'slug': self.kwargs['slug']})