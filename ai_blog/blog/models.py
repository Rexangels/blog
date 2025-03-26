# blog/models.py
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
from ckeditor_uploader.fields import RichTextUploadingField

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

    title = models.CharField(max_length=200, verbose_name='Post Title')
    slug = models.SlugField(unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = RichTextUploadingField(verbose_name='Post Content')
    
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

    # Tracking and Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    view_count = models.PositiveIntegerField(default=0)
    
    # Relationships
    categories = models.ManyToManyField(Category, related_name='posts')
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')
    
    # Media
    featured_image = models.ImageField(
        upload_to='posts/', 
        blank=True, 
        null=True, 
        verbose_name='Featured Image'
    )

    # Visibility Control
    visibility = models.CharField(
        max_length=10, 
        choices=VISIBILITY_CHOICES, 
        default='public'
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'slug': self.slug})

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