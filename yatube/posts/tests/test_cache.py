from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache
from ..models import Post

User = get_user_model()


class CacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Saycoron')

    def setUp(self):
        self.guest_client = Client()
        cache.clear()

    def test_cache(self):
        first_response = self.guest_client.get(reverse('posts:index'))
        post = Post.objects.create(
            author=self.user,
            text='Тестовый пост достаточной длины',
        )
        second_response = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(first_response.content, second_response.content)
        cache.clear()
        third_response = self.guest_client.get(reverse('posts:index'))
        self.assertNotEqual(first_response.content, third_response.content)
        post.delete()
        fourth_response = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(third_response.content, fourth_response.content)
        cache.clear()
        fifth_response = self.guest_client.get(reverse('posts:index'))
        self.assertNotEqual(fifth_response.content, fourth_response.content)

