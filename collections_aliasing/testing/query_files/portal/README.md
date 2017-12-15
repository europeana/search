# Testing the Europeana Collections Portal

These files are for basic sanity-checking and testing of the Solr backend powering [Europeana Collections](https://www.europeana.eu/portal/en).

The required settings are as follows:

* Query Mode: Standard
* Use Facets: true
* Use SolrCloud: true
* ZooKeeper Chroot: /
* Use Filter Queries: true
* Facet Method: fc
* Force echoParam=all: false

The various File Path settings should be pointed at the appropriate files within this directory.

The Solr and Zookeeper parameters required will of course vary with the installation being tested. As of 2017.12.15, the appropriate settings were:

URL Zookeeper: sol7.eanadev.org
Default Solr Collection: search_production_publish_1
