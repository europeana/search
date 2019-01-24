from django.db import models

MAX_QUERY_LENGTH = 255

class Query(models.Model):

    query_text = models.CharField('query text', max_length=MAX_QUERY_LENGTH, unique=True)

    def __str__(self):
        return self.query_text

    class Meta:
        verbose_name_plural = "query"

class CandidateBoostFields(models.Model):
    field_name = models.CharField('field name', max_length=50, unique=True)