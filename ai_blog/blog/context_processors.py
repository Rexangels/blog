from .models import AdSpace,Newsletter
from .forms import NewsletterForm


def global_context(request):
    
    return {
        'header_ads': AdSpace.objects.filter(is_active=True, location='header'),
        'sidebar_ads': AdSpace.objects.filter(is_active=True, location='sidebar'),
        'between_posts_ads': AdSpace.objects.filter(is_active=True, location='between_posts'),
        'footer_ads': AdSpace.objects.filter(is_active=True, location='footer'),
        'newsletter_form': NewsletterForm(),
    }