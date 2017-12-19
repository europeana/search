# Collections Aliasing Solr Extension

## Motivation

The purpose of this plugin is to allow users to define shorthand aliases for complex queries. The most frequent use case for such aliases at Europeana is for defining our thematic collections.

Such queries can be long and convoluted, creating two problems:

1. They are not readily reproducible by API clients. Anyone wishing to retrieve the contents of a thematic collection must replicate the entire query. These queries, however, are not documented, are not entirely stable, and are extremely complex. Providing a simple alias for collection retrieval is the only really viable means for offering API clients a means of accessing them.

2. The size of the thematic collections means that they need to be cached - that is to say, included in Solr's internal list of cache-warming queries. The length and complexity of the queries makes this an error-prone and fiddly process. In addition, Solr must be restarted (that is to say, new Searchers need to be initialised) every time a new thematic collection query is created or an old one updated.

## Using the Solr Extension

1. Queries and their aliases are defined in the `query_aliases.xml` configuration file. The syntax is simple: the `alias-pseudofield` element holds the name of the artificial field used to access the aliases; the `alias` element gives the alias; and the `query` element holds the full query. 

    For example, if we wanted clients to be able to access the Europeana Art collection with the query 'collection:art', the value of the `alias-pseudofield` would be 'collection', the `alias` would be 'art', and the `query` element would be used to hold the full query used to create the thematic collection. 

2. To ensure that cache-warming takes place, new thematic collections need to be added to the `firstSearcher` and `newSearcher` events in the `solrconfig.xml` file, using their aliases. So, for instance, in the example given above, we would have to add the query 'fq=collection:art' to the file.

    Note that once this query has been added, we do not need to change the `solrconfig.xml` file when the query is updated; we simply change the query in the `query_aliases.xml` file.

## Deploying the Solr Extension

### Configuration

Aliasing is handled by the [`Aliasing Request Handler`](https://github.com/europeana/search/blob/master/collections_aliasing/solr-4.10.4/solr/core/src/java/org/apache/solr/handler/component/AliasingRequestHandler.java). This means that a reference to the handler must be made available in `solrconfig.xml`.

Note that because the aliasing functionality is supplied by a `RequestHandler` rather than a `SearchComponent`, it is essentially "wrapping" our other search functionality. In particular, the BM25f `SearchComponent` can be used with the aliasing function intact. This can be seen in the [default handler](https://github.com/europeana/search/blob/master/current_confs/search_api/conf/solrconfig.xml#L1156) of the deployed extension.

### Compilation

Implementing the aliasing functionality involves changes at two points.

1. **Configuration loading:** At startup, the `query_aliases.xml` file needs to be loaded and the information it contains made available to the Solr core. This task is performed by the [`AliasConfig` class](https://github.com/europeana/search/blob/master/collections_aliasing/solr-4.10.4/solr/core/src/java/org/apache/solr/core/AliasConfig.java).

2. **Extended Request Handling:** As described above, aliasing at query-time is provided by the `AliasingRequestHandler` plugin.

Because the first change extends core Solr functionality (that is to say, it falls outside Solr's plugin-based architecture for user extesions), deploying the aliasing functionality will involve compiling Solr from source. Depending on on the exact character of the deployment, it may be possible to deploy these changes essentially as though they constituted a plugin (albeit one using the `solr.core` package); but YMMV. 

### Querying using aliases

This is simple: querying can be done using standard Solr syntax, with the handler swapping in the expanded queries behind the scenes as appropriate. Any string defined in an `alias-pseudofield` element in the [query_aliases.xml](https://github.com/europeana/search/blob/master/current_confs/search_api/conf/query_aliases.xml) document can be used as though it were a field; and it will accept any value defined in the `alias` element as though it were a value of that field. For example, using the [deployed query_aliases.xml](https://github.com/europeana/search/blob/master/current_confs/search_api/conf/query_aliases.xml) document, it is possible to use the term 'collection' as though it were a field defined in the `schema.xml` document, with values 'art', 'music', 'photography', etc.

If the client submits a field that is defined neither in the `schema.xml` document nor in the `query_aliases.xml` file, it will fail silently (as Solr normally does with undefined fields with the deployed configuration). If the user attempts to use an alias which is not defined, a 400 error will be returned with the message that the alias is undefined.

