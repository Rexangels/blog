from django.test import TestCase

# Create your tests here.
# blog/tests.py
from django.test import TestCase
from django.contrib.auth.models import User
from .models import Post

class PostModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser")
        self.post = Post.objects.create(
            title="Test Post",
            slug="test-post",
            author=self.user,
            content="Test content for the post."
        )

    def test_post_creation(self):
        self.assertEqual(str(self.post), "Test Post")
