from django.db import models
from django.utils import timezone
class Post(models.Model):
    title = models.CharField("Заголовок", max_length=200)
    id = models.BigAutoField(primary_key=True)
    content = models.TextField("Содержимое")
    created_at = models.DateTimeField("Дата публикации", default=timezone.now)