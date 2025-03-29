# blog/views.py
from .models import Post, Category, Tag, Newsletter, AdSpace, Comment
from .forms import PostForm, NewsletterForm, CommentForm
from django.views.generic import ( 
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count
from django.urls import reverse_lazy
from django.urls import reverse_lazy
from .models import Post, Category, Tag, Newsletter, AdSpace
class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        # Filter for public posts and annotate with comment count
        return Post.objects.filter(visibility='public').annotate(
            comment_count=Count('comments')
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['tags'] = Tag.objects.all()
        context['top_posts'] = Post.objects.filter(visibility='public').order_by('-view_count')[:5]
        context['ads'] = AdSpace.objects.filter(is_active=True)
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
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_posts'] = Post.objects.filter(
            categories__in=self.object.categories.all()
        ).exclude(pk=self.object.pk)[:3]
        return context

class PostCreateView(CreateView):
    model = Post
    form_class = PostForm
    success_url = reverse_lazy('blog:home')

class AdvancedSearchView(ListView):
    model = Post
    template_name = 'blog/search_results.html'
    context_object_name = 'posts'

    def get_queryset(self):
        query = self.request.GET.get('q')
        category = self.request.GET.get('category')
        tags = self.request.GET.getlist('tags')
        
        queryset = Post.objects.filter(visibility='public')
        
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | 
                Q(content__icontains=query)
            )
        
        if category:
            queryset = queryset.filter(categories__slug=category)
        
        if tags:
            queryset = queryset.filter(tags__slug__in=tags)
        
        return queryset.order_by('-created_at')

class NewsletterSignupView(CreateView):
    model = Newsletter
    form_class = NewsletterForm
    template_name = 'blog/newsletter_signup.html'
    success_url = reverse_lazy('blog:home')

    def form_valid(self, form):
        # Additional logic like sending welcome email
        response = super().form_valid(form)
        # Implement email service integration here
        return response

# Add to blog/views.py
class CommentCreateView(CreateView):
    model = Comment
    form_class = CommentForm
    
    def form_valid(self, form):
        form.instance.post = Post.objects.get(slug=self.kwargs['slug'])
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'slug': self.kwargs['slug']})