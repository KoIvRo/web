from django.db import models
from django.utils import timezone
from django.utils.text import slugify

class Post(models.Model):
    title = models.CharField("Заголовок", max_length=200)
    slug = models.SlugField("URL", unique=True)
    content = models.TextField("Содержимое")
    created_at = models.DateTimeField("Дата публикации", default=timezone.now)