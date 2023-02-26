from core.models import CreatedModel
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Post(CreatedModel):
    text = models.TextField('текст поста',
                            help_text='Введите текст поста')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='posts',
                               verbose_name='автор')
    group = models.ForeignKey('Group',
                              blank=True,
                              null=True,
                              on_delete=models.SET_NULL,
                              related_name='group_posts',
                              verbose_name='группа',
                              help_text='Выберите группу')
    image = models.ImageField('Картинка',
                              upload_to='posts/',
                              blank=True)

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:15]


class Group(models.Model):
    title = models.CharField('название группы', max_length=200)
    slug = models.SlugField('заголовок-ссылка', unique=True, null=False)
    description = models.TextField('описание', max_length=300)

    def __str__(self):
        return self.title


class Comment(CreatedModel):
    post = models.ForeignKey(Post,
                             related_name='comments',
                             on_delete=models.CASCADE)
    author = models.ForeignKey(User,
                               related_name='comments',
                               on_delete=models.CASCADE)
    text = models.TextField('текст комментария',
                            help_text='Оставьте комментарий')


class Follow(models.Model):
    user = models.ForeignKey(User,
                             related_name='follower',
                             on_delete=models.CASCADE)
    author = models.ForeignKey(User,
                               related_name='following',
                               on_delete=models.CASCADE)
