from django.db import models

# Create your models here.

class InitialItem(models.Model):
    europeana_id = models.CharField(max_length=250)
    title = models.CharField(max_length=500)
    description = models.TextField()
    resource_type = models.CharField(max_length=20)
    thumbnail = models.URLField(max_length=350)
    url = models.URLField(max_length=250)
    original_page = models.URLField(max_length=350, default="www.example.com")
    data_provider = models.CharField(max_length=150, default="rj")

class FieldName(models.Model):
    field_name = models.CharField(max_length=75)