from django.contrib import admin

from .models import Query, QueryComment, QueryMotive, Language

admin.site.register(Query)
admin.site.register(QueryComment)
admin.site.register(QueryMotive)
admin.site.register(Language)

