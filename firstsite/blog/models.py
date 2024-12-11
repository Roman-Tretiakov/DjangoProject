from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status='published')


class Post(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )

    title = models.CharField(max_length=250)  # заголовок статьи
    slug = models.SlugField(max_length=250, unique_for_date='publish')  # URL статьи, используя уникальную дату статьи
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')  # Внешний ключ один ко многим
    body = models.TextField()  # содержание статьи
    publish = models.DateTimeField(default=timezone.now)  # дата публикации статьи
    created = models.DateTimeField(auto_now_add=True)  # Дата создания статьи
    updated = models.DateTimeField(auto_now_add=True)  # дата и период, когда статья была отредактирована
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')  # статус статьи
    objects = models.Manager()  # Менеджер по умолчанию
    published = PublishedManager()  # Наш новый менеджер

    def get_absolute_url(self):
        # noinspection PyUnresolvedReferences
        return reverse('blog:post_detail', args=[self.publish.year, self.publish.month, self.publish.day,
                                                 self.slug])

    class Meta:
        ordering = ('-publish',)  # метаданные в порядке убывания (префикс -)

    def __str__(self):
        return self.title  # Возвращает отображение, понятное для человека

