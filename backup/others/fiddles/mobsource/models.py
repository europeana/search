from django.db import models
from django.db.models import Field
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator

REQD_RESULTS = 10
MAX_RELEVANCE = 5

class Query(models.Model):
    """ The query itself; the key object
    """
    query_text = models.CharField('query text', max_length=255, unique=True)
    source = models.ForeignKey(User, related_name='query_by')
    language = models.ForeignKey('Language', related_name='target_language')
    ndcg = models.DecimalField(max_digits=4, decimal_places=3, null=True)

    def __str__(self):
        return self.query_text

    class Meta:
        verbose_name_plural = "queries"

class QueryMotive(models.Model):
    """ The information need behind the Query. 0 or 1 per Query.
    """
    motive_text = models.TextField(blank=True)
    query = models.OneToOneField(Query)

    def __str__(self):
        return self.motive_text

class QueryComment(models.Model):
    """ Any comment on the results returned to the user. 0 or 1 per Query.
    """
    comment_text = models.TextField(blank=True)
    query = models.OneToOneField(Query)

    def __str__(self):
        return self.comment_text

class Language(models.Model):
    """ The language of the query. 1 per query.
    """
    language = models.CharField(max_length=30)
    language_code = models.CharField(max_length=3)

    def __str__(self):
        return self.language

class QueryResult(models.Model):
    """ A result returned in response to a query.

        The number of QueryResults per Query must be greater than 1
        and at most 10.
    """

    validate_rating = MaxValueValidator(MAX_RELEVANCE)
    validate_position = MaxValueValidator(REQD_RESULTS)
    query = models.ForeignKey(Query, related_name='response_to')
    europeana_id = models.CharField(max_length=255)
    position = models.PositiveSmallIntegerField(blank=False, validators=[validate_position])
    rating = models.PositiveSmallIntegerField(blank=False, validators=[validate_rating])
    timestamp = models.DateTimeField(null=True, auto_now_add=True)

def ndcg(result_list, items=REQD_RESULTS, max_score=MAX_RELEVANCE):
    best_list = [ max_score for dummy in range(items)]
    max_dcg = dcg(best_list, items)
    real_dcg = dcg(result_list, items)
    return real_dcg / max_dcg

def dcg(result_list, items):
    from functools import reduce
    return reduce(lambda x, y: x + y, [ dg(result) for result in enumerate(result_list[0:items])])

def dg(result):
    from math import log2
    position = result[0] + 1         # position must be 1-indexed
    relevance = (2 * result[1]) or 1 # ensure no negative result when 1 deducted
    gain = relevance - 1
    discount = log2(position + 1)
    return gain / discount