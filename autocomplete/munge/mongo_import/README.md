# Mongo Import

Python scripts for porting MongoDB data to Solr for the Entity Collection

## Dependencies

### Celery

Celery relies upon a (Redis|http://redis.io) server running on 6379 to act as message broker.

One implication of this is that the Celery libraries for Redis must also be installed. If using pip, this can be done with `pip3 install -U celery[redis]`.

TODO: Celery daemonization