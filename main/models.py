from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Post(models.Model):
    title = models.CharField("Заголовок", max_length=200)
    id = models.BigAutoField(primary_key=True)
    content = models.TextField("Содержимое")
    created_at = models.DateTimeField("Дата публикации", default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    CATEGORY_CHOICES = [
        ('programming', 'Программирование'),
        ('django', 'Django'),
        ('python', 'Python'),
        ('web', 'Веб-разработка'),
        ('other', 'Другое'),
    ]
    category = models.CharField(
        "Категория",
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='other'
    )

class Comment(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField("Дата публикации", default=timezone.now)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments' )
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField("Содержимое")

    class Meta:
        ordering = ["-created_at"]