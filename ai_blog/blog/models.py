# blog/models.py
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
from ckeditor_uploader.fields import RichTextUploadingField

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone
from ckeditor_uploader.fields import RichTextUploadingField
import readtime

# Add to blog/models.py
from django.db.models.signals import post_save
from django.dispatch import receiver

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Category Name')
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:category_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.name

class Series(models.Model):
    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Post(models.Model):
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
        ('draft', 'Draft')
    ]
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),  # Added archived status
    )

    title = models.CharField(max_length=200, verbose_name='Post Title')
    slug = models.SlugField(unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = RichTextUploadingField()
    
    # SEO Fields
    meta_description = models.TextField(
        max_length=160, 
        blank=True,
        help_text="Short description for SEO (max 160 characters)"
    )
    seo_keywords = models.CharField(
        max_length=255, 
        blank=True, 
        help_text="Comma-separated SEO keywords"
    )
    
    # Featured control
    is_featured = models.BooleanField(default=False, help_text="Feature this post on the homepage")
    is_pinned = models.BooleanField(default=False, help_text="Pin this post to the top of lists")
    
    # Tracking and Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    view_count = models.PositiveIntegerField(default=0)
    like_count = models.PositiveIntegerField(default=0)
    bookmark_count = models.PositiveIntegerField(default=0)
    estimated_reading_time = models.PositiveIntegerField(default=0, editable=False, 
                                                        help_text="Estimated reading time in minutes")
    
    # Soft delete
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    # Relationships
    categories = models.ManyToManyField('Category', related_name='posts')
    series = models.ForeignKey(Series, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    tags = models.ManyToManyField('Tag', blank=True, related_name='posts')
    
    # Media
    featured_image = models.ImageField(
        upload_to='posts/', 
        blank=True, 
        null=True, 
        verbose_name='Featured Image'
    )
    
    # Table of contents
    show_table_of_contents = models.BooleanField(default=True)
    
    # Visibility Control
    visibility = models.CharField(
        max_length=10, 
        choices=VISIBILITY_CHOICES, 
        default='public'
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    published_date = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-is_pinned', '-published_date', '-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['status', 'visibility']),
            models.Index(fields=['published_date']),
            models.Index(fields=['-is_pinned', '-published_date']),
        ]
    
    def save(self, *args, **kwargs):
        # Generate slug if not provided
        if not self.slug:
            self.slug = slugify(self.title)
            
            # Check for slug conflicts and make unique if needed
            original_slug = self.slug
            counter = 1
            while Post.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        
        # Calculate reading time before saving
        if self.content:
            result = readtime.of_text(self.content)
            self.estimated_reading_time = result.minutes
        
        # Set published date if publishing
        if self.status == 'published' and not self.published_date:
            self.published_date = timezone.now()
            
        super().save(*args, **kwargs)
    
    def soft_delete(self):
        """Soft delete the post instead of hard deleting"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()
    
    def restore(self):
        """Restore a soft-deleted post"""
        self.is_deleted = False
        self.deleted_at = None
        self.save()
    
    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'slug': self.slug})
    
    def get_like_url(self):
        return reverse('blog:post_like', kwargs={'slug': self.slug})
    
    def get_bookmark_url(self):
        return reverse('blog:post_bookmark', kwargs={'slug': self.slug})
    
    def get_share_url(self):
        return reverse('blog:post_share', kwargs={'slug': self.slug})
        
    def __str__(self):
        return self.title

class AdSpace(models.Model):
    LOCATION_CHOICES = [
        ('header', 'Header'),
        ('sidebar', 'Sidebar'),
        ('between_posts', 'Between Posts'),
        ('footer', 'Footer')
    ]
    
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=20, choices=LOCATION_CHOICES)
    ad_code = models.TextField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} - {self.location}"

class Newsletter(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.email

class SponsoredContent(models.Model):
    title = models.CharField(max_length=200)
    content = RichTextUploadingField()
    sponsor = models.CharField(max_length=100)
    sponsored_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.title} - Sponsored by {self.sponsor}"

# Add to blog/models.py
class Comment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('spam', 'Spam'),
        ('deleted', 'Deleted')
    )
    
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.CharField(max_length=100)
    email = models.EmailField(blank=True)  # Optional email for notification
    website = models.URLField(blank=True)  # Optional website field
    
    # Support for nested comments
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    content = models.TextField()
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    
    # User info if comment is by a registered user
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='comments')
    
    # IP and user agent for moderation/spam prevention
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    
    # CHANGED: Renamed to 'like_count' to avoid clash with CommentLike related_name
    like_count = models.PositiveIntegerField(default=0)
    
    # For ordering - lets you pin important comments
    is_pinned = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-is_pinned', 'created_at']
        indexes = [
            models.Index(fields=['post', 'status']),
            models.Index(fields=['user']),
            models.Index(fields=['parent']),
        ]
    
    def __str__(self):
        if self.user:
            author = self.user.username
        else:
            author = self.author
            
        return f"Comment by {author} on {self.post.title}"
    
    @property
    def is_reply(self):
        """Check if this comment is a reply to another comment"""
        return self.parent is not None
    
    def approve(self):
        """Approve the comment"""
        self.status = 'approved'
        self.save()
    
    def mark_as_spam(self):
        """Mark the comment as spam"""
        self.status = 'spam'
        self.save()


# Add to blog/models.py
class PageVisit(models.Model):
    page_url = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True, null=True)
    visited_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Visit to {self.page_url} at {self.visited_at}"



class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='blog_profile')
    bio = models.TextField(blank=True, max_length=500)
    avatar = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    website = models.URLField(blank=True)
    twitter = models.CharField(max_length=50, blank=True)
    github = models.CharField(max_length=50, blank=True)
    linkedin = models.CharField(max_length=50, blank=True)
    display_name = models.CharField(max_length=50, blank=True)
    location = models.CharField(max_length=100, blank=True)
    
    # For notifications - enable/disable options
    email_notifications = models.BooleanField(default=True)
    notify_on_comment = models.BooleanField(default=True)
    notify_on_reply = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s profile"
    
    def get_absolute_url(self):
        return reverse('blog:user_profile', kwargs={'username': self.user.username})

# Update signal handlers to use the new related_name
@receiver(post_save, sender=User)
def create_user_blog_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_blog_profile(sender, instance, **kwargs):
    if hasattr(instance, 'blog_profile'):
        instance.blog_profile.save()


# Add to blog/models.py

class PostLike(models.Model):
    """Model to track users liking posts"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'post')
        
    def __str__(self):
        return f"{self.user.username} liked {self.post.title}"

class Bookmark(models.Model):
    """Model for users to bookmark posts to read later"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='bookmarks')
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, help_text="Personal notes about this bookmark")
    
    class Meta:
        unique_together = ('user', 'post')
        
    def __str__(self):
        return f"{self.user.username} bookmarked {self.post.title}"


class CommentLike(models.Model):
    """Model to track users liking comments"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_likes')
    # CHANGED: Updated related_name to 'comment_likes' to avoid clash with Comment.likes field
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='comment_likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'comment')
        
    def __str__(self):
        return f"{self.user.username} liked a comment"