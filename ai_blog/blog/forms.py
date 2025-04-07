# blog/forms.py
from django import forms
from django.utils.text import slugify
from .models import UserProfile, UserNotificationSettings
from .models import Post, Newsletter, Series


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'categories', 'tags', 'featured_image', 'series']
        
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'categories': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }

        widgets['series'] = forms.Select(attrs={'class': 'form-control'})
    def clean_title(self):
        title = self.cleaned_data['title']
        if len(title) < 5:
            raise forms.ValidationError("Title must be at least 5 characters long")
        return title

    def clean_content(self):
        content = self.cleaned_data['content']
        if len(content) < 20:
            raise forms.ValidationError("Content must be at least 20 characters long")
        return content

    def generate_unique_slug(self, title):
        """
        Generate a unique slug based on the title
        """
        base_slug = slugify(title)
        unique_slug = base_slug
        n = 1
        from .models import Post
        while Post.objects.filter(slug=unique_slug).exists():
            unique_slug = f"{base_slug}-{n}"
            n += 1
        return unique_slug

    def save(self, commit=True):
        # Generate slug before saving
        instance = super().save(commit=False)
        if not instance.slug:
            instance.slug = self.generate_unique_slug(instance.title)
        
        if commit:
            instance.save()
        return instance
    
from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['author', 'content']
        widgets = {
            'author': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class NewsletterForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'placeholder': 'Enter your email',
                'class': 'form-control'
            })
        }

    def clean_email(self):
        email = self.cleaned_data['email']
        if Newsletter.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already subscribed")
        return email

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'location', 'website', 'twitter', 'github', 'linkedin', 'avatar']
        widgets = {
            'avatar': forms.ClearableFileInput(),
        }

class UserNotificationSettingsForm(forms.ModelForm):
    class Meta:
        model = UserNotificationSettings
        fields = ['receive_post_notifications', 'receive_comment_notifications', 'receive_series_notifications']




