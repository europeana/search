# Mongo Import

Python scripts for porting MongoDB data to Solr for the Entity Collection

## Dependencies

### Python

#### Version

Python 3.x is required.

#### Packages

Extensive use is made of the [PyMongo](https://api.mongodb.com/python/current/), [Celery](http://www.celeryproject.org/), and [requests](http://docs.python-requests.org/en/master/) libraries.

### Celery

Celery relies upon a [Redis](http://redis.io) server running on 6379 to act as message broker.

One implication of this is that the Celery libraries for Redis must also be installed. If using pip, this can be done with `pip3 install -U celery[redis]`.

#### Celery configuration

The Celery tasks are defined in `tasks.py`, and invoked using `celeryclient.py`. "Configuration" of `celeryclient.py` is done simply through (un)commenting lines, at the moment.

## Solr Configuration

Autosuggest is implemented using Solr's built-in [Suggester](https://cwiki.apache.org/confluence/display/solr/Suggester) functionality. This is configured in the [solrconfig.xml](https://github.com/europeana/search/blob/master/autocomplete/conf/solrconfig.xml) file.

The Autosuggest handler is invoked using the `/suggestEntity` path. This returns suggestions in *all* supported languages. To limit suggestions to a given language, append that languages ISO 639-1 code to the handler (so that, for example, French suggestions are supplied by `suggestEntity/fr`).

Note the simple field structures used by the Suggester: suggestions are made from the `skos_prefLabel` field (language-qualified as appropriate); the absolute relevance ranking is stored in `derived_score`; and the entity preview is stored in `payload`. All other fields are ignored by the Suggester (though they may of course be retrieved through other handlers).

## Python Code Structure

The code structure is, in broad overview, extremely simple. Harvesting of entities from the MongoDB instance is performed by the appropriate subclass of `ContextClassHarvester` (so, for Agents, `AgentHarvester`, Places, `PlaceHarvester`, etc.)

Each `ContextClassHarvester` has a `LanguageValidator`, which ensures that only entries conformant to ISO 639-1 are harvested from the MongoDB.

In addition, each `ContextClassHarvester` has a `RelevanceCounter`, which calculates relevance metrics, and a `PreviewBuilder`. This, as the name implies, creates the JSON structure necessary to support the entity preview found in the `payload` field.

For further information, see code comments inline.



