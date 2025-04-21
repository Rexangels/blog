from django.contrib.syndication.views import Feed
from django.urls import reverse_lazy
from django.utils.feedgenerator import Rss201rev2Feed
from .models import Post


class LatestPostsFeed(Feed):
    """
    RSS feed for the latest blog posts
    """
    feed_type = Rss201rev2Feed
    title = "AI & Programming Blog"
    link = reverse_lazy("blog:home")
    description = "Latest articles on artificial intelligence, programming, and technology."
    
    def items(self):
        """Return the most recent published posts."""
        return Post.objects.filter(status=Post.Status.PUBLISHED).order_by("-publish_date")[:15]
    
    def item_title(self, item):
        """Return the title of the post."""
        return item.title
    
    def item_description(self, item):
        """Return the description (excerpt) of the post."""
        return item.excerpt or item.content[:200] + "..."
    
    def item_link(self, item):
        """Return the URL to the post."""
        return reverse_lazy("blog:post_detail", args=[item.slug])
    
    def item_author_name(self, item):
        """Return the author's name."""
        return item.author.get_full_name() or item.author.username
    
    def item_pubdate(self, item):
        """Return the publication date."""
        return item.publish_date
    
    def item_categories(self, item):
        """Return the post's categories."""
        return [category.name for category in item.categories.all()]