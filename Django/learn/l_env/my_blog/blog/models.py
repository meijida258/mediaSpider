from django.db import models
class Article(models.Model):
    first_name = models.CharField(max_length=10)
    class Meta:
        db_table = 'article'

    def __str__(self):
        return self.first_name
# Create your models here.
