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

import pytest
from django.contrib.auth.models import User
from .models import Post, Category, Tag

@pytest.mark.django_db
def test_post_creation():
    """Test that a Post instance can be created."""
    # Arrange
    user = User.objects.create_user(username='testuser', password='password')
    category = Category.objects.create(name='Test Category', slug='test-category')
    
    # Act
    post = Post.objects.create(
        title='Test Post Title',
        content='This is the test content.',
        author=user,
        status='published',
        visibility='public'
    )
    post.categories.add(category)

    # Assert
    assert Post.objects.count() == 1
    assert post.title == 'Test Post Title'
    assert post.author.username == 'testuser'
    assert post.status == 'published'
    assert post.categories.count() == 1
    assert post.categories.first().name == 'Test Category'
    assert str(post) == 'Test Post Title' # Assuming __str__ returns the title

@pytest.mark.django_db
def test_category_creation():
    """Test that a Category instance can be created."""
    # Act
    category = Category.objects.create(name='Technology', slug='technology')

    # Assert
    assert Category.objects.count() == 1
    assert category.name == 'Technology'
    assert category.slug == 'technology'
    assert str(category) == 'Technology' # Assuming __str__ returns the name

@pytest.mark.django_db
def test_tag_creation():
    """Test that a Tag instance can be created."""
    # Act
    tag = Tag.objects.create(name='Python', slug='python')

    # Assert
    assert Tag.objects.count() == 1
    assert tag.name == 'Python'
    assert tag.slug == 'python'
    assert str(tag) == 'Python' # Assuming __str__ returns the name

# You can add more tests here for other models or functionalities
