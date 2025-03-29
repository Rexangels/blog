# blog/admin.py
from django.contrib import admin
# Update blog/admin.py to include missing models
from .models import Post, Category, Tag, Newsletter, SponsoredContent, AdSpace, Comment

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'updated_at')
    list_filter = ('created_at', 'categories', 'tags')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


# Add these registrations
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'created_at')
    search_fields = ('content', 'author')
    list_filter = ('created_at',)

@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed_at', 'is_active')
    search_fields = ('email',)
    list_filter = ('is_active', 'subscribed_at')

@admin.register(SponsoredContent)
class SponsoredContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'sponsor', 'sponsored_date', 'is_active')
    search_fields = ('title', 'sponsor', 'content')
    list_filter = ('is_active', 'sponsored_date')

@admin.register(AdSpace)
class AdSpaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'is_active')
    list_filter = ('location', 'is_active')