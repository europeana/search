# Collections Aliasing Plugin

The purpose of this plugin is to allow users to define shorthand aliases for complex queries.

These queries are defined in the query_aliases.xml configuration file. Such aliases can then be used:

1. In the solrconfig.xml file to refer to queries to be run for cache-warming purposes.
2. Over the Solr REST API, to be expanded by Solr as required.


