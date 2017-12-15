# Testing the Entity Collection Solr cores

These files are for basic sanity-checking and testing of the Solr backend and associated Solr installations powering the [Entity API](https://pro.europeana.eu/resources/apis/entity).

The required settings are as follows:

* Query Mode: Standard
* Use Facets: true
* Use SolrCloud: false
* Use Filter Queries: true
* Facet Method: fc
* Force echoParam=all: false

The various File Path settings should be pointed at the appropriate files within this directory. 

The Solr and Zookeeper parameters required will of course vary with the installation being tested. As of 2017.12.15, the appropriate Solr cores to test were:

* Acceptance - at http://entity-acceptance.eanadev.org:9191/solr/acceptance
* Test - at http://entity-api.eanadev.org:9292/solr/test
* Production - at http://entity-api.eanadev.org:9191/solr/production
