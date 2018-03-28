# Entity Collection Ranking

The ranking metrics currently used for ordering Entity Collection entities for search and autocomplete are quite simple. The formula is described in more detail in the Integrating Wikidata PageRank metrics into EC relevance [Basecamp thread](https://basecamp.com/1768384/projects/5774755/messages/69533346#comment_533893612).

The important point to note, however, is that in fact only two signals are used for calculating relevance: the number of hits a given entity's identifier has in Europeana, and the PageRank of that entity in Wikidata. While there will on occasion be references in code to other signals, these are now deprecated in favour of this simple pair of measures.

# Harvesting the Relevance Metrics

Note that harvesting the relevance signals is a relatively expensive process. For this reason, such harvesting is performed separately and in advance of running the import scripts. If this dual procedure were not used, every complete entity rebuild would take several hours - instead of a couple of minutes, as now. 

The procedure for harvesting the relevance metrics is as follows;

1. Entities are retrieved from the relevant Mongo datastore
2. The identifiers of these entities are used to query the Collections Solr datastore
3. A mapping operation takes place to align our own identifiers with the Wikidata identifiers used in the Wikidata PageRank archive. The Wikidata identifier is then used to retrieve the relevant PageRank score.
4. The entity identifier, number of Europeana hits, and PageRank are then all written to the relevant SQLite file in the `../db directory`.

For the moment, all these steps are completed using ad hoc scripts. This is because the sources of our entities and the procedures for harvesting them have not yet stabilised: data is drawn from several different sources, and it is therefore currently impossible to take a completely standardised approach. The `populate_metrics_dbs.py` and `populate_organization_db.py` scripts (both in the `resources` directory) may provide some guidance. But their utility is illustrative only. 

## Wikidata PageRank

Our source for Wikidata PageRank values comes from the [research](http://www.aifb.kit.edu/images/e/e5/Wikipedia_pagerank1.pdf) of Andreas Thalhammer and Achim Rettinger. It is provided as a [BZip2 TSV file](https://drive.google.com/open?id=11U7SL1kbyNaWdmQbvbqg5k1b04Nv7v0v) listing Wikidata identifiers and their calculated PageRank values.

## SQLite databases

There are currently four SQLite databases, one for each entity type in the Entity Collection. They all have an identical structure, containing a single table called 'hits' with the following schema:
```
id VARCHAR(200) PRIMARY KEY,
wikipedia_hits INTEGER,
europeana_enrichment_hits INTEGER,
europeana_string_hits INTEGER,
pagerank REAL
```

Note that the `wikipedia_hits` and `europeana_string_hits` values are no longer used as relevance signals, and can thus simply be populated with 0 or NULL values.