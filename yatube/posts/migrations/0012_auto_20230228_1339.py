# Generated by Django 2.2.16 on 2023-02-28 13:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0011_follow'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ('-pub_date',), 'verbose_name': 'Пост', 'verbose_name_plural': 'Посты'},
        ),
        migrations.AddIndex(
            model_name='group',
            index=models.Index(fields=['slug'], name='slug_idx'),
        ),
    ]
