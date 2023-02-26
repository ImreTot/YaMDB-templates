import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Saycoron')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'group': self.group.id,
            'text': 'Тестовый пост достаточной длины',
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': 'Saycoron'}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый пост достаточной длины',
                author=self.user,
                group=self.group.id
            ).exists()
        )

    def test_edit_post(self):
        """Валидная форма изменяет запись в Post."""
        post = Post.objects.create(
            author=self.user,
            text='Тестовый пост достаточной длины',
            group=self.group
        )
        posts_count = Post.objects.count()
        another_group = Group.objects.create(
            title='Другая тестовая группа',
            slug='another_test-slug',
            description='Еще одно тестовое описание',
        )
        form_data = {
            'text': 'Другой тестовый пост достаточной длины',
            'group': another_group.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={
                'post_id': post.id
            }),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': post.id}
        ))
        post.refresh_from_db()
        self.assertNotEqual(
            Post.objects.get(id=post.id).text,
            'Тестовый пост достаточной длины')
        self.assertEqual(post.author, self.user)
        self.assertEqual(Post.objects.count(), posts_count)

    def test_guest_client_create_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост достаточной длины',
        }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, '/auth/login/?next=/create/')
        self.assertEqual(Post.objects.count(), posts_count)

    def test_comments_appear_on_post_detail(self):
        """Тестовый комментарий появляется под соответствующим постом."""
        post = Post.objects.create(
            author=self.user,
            text='Тестовый пост достаточной длины',
            group=self.group
        )
        comments_count = Comment.objects.filter(post_id=post.id).count()
        form_data = {'text': 'тестовый комментарий.'}
        self.authorized_client.get(reverse(
            'posts:add_comment',
            kwargs={'post_id': post.id}),
            form=form_data,
            follow=True
        )
        self.assertEqual(comments_count,
                         Comment.objects.filter(post_id=post.id).count())
