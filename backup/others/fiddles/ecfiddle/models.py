from django.db import models

class CandidateField(models.Model):

    field_name = models.CharField('field name', max_length=150, unique=True)


