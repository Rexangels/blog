from .models import AdSpace, Newsletter, Notification
from .forms import NewsletterForm  


def global_context(request):
    
    return {
        'header_ads': AdSpace.objects.filter(is_active=True, location='header'),
        'sidebar_ads': AdSpace.objects.filter(is_active=True, location='sidebar'),
        'between_posts_ads': AdSpace.objects.filter(is_active=True, location='between_posts'),
        'footer_ads': AdSpace.objects.filter(is_active=True, location='footer'),
        'newsletter_form': NewsletterForm(),
    }


def notifications(request):
    """Context processor to add unread notifications to the context."""
    if request.user.is_authenticated:
        unread_notifications = Notification.objects.filter(
            user=request.user, is_read=False
        ).order_by('-created_at')
    else:
        unread_notifications = []
    return {'notifications': unread_notifications}