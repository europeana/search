# Solr Search Handler Plugin for Query Aliasing

The code was originally developed within the Europeana Project (see https://github.com/europeana/search/tree/master/collections_aliasing). The original code was for Solr version 4.10 and involved recompiling a bespoke version of the entire Solr code. 

This code was developed for Solr version 6.6, and with a few migration changes should be straightforward to convert to later Solr versions.  

The current functionality "should" be identical to the original handler, the only difference to the Solr configuration being that the class name was changed from AliasingRequestHandler to AliasingSearchHandler (as the class extends SearchHandler). 

## Installation

Compile a jar using the command "mvn package"

Copy the resultant jar in the target directory to the solr home directory.

To include the jar in the core add the following line to the core's solrconfig.xml file:

    <lib dir="../lib" regex=".*\.jar" />
  
There are then two (mutually exclusive) ways of using the aliasing; as a SearchHandler or a QueryComponent.

### Installing as Search Handler

To use the request handler add the following line to the core's solrconfig.xml file:

    <requestHandler name="/alias" class="solr.AliasingSearchHandler"/>

If you wish to replace the default "select"  handler then just replace the "solr.SearchHandler" class name with "solr.AliasingSearchHandler"

### Installing as Query Component

To use the request handler add the following line to the core's solrconfig.xml file:

     <searchComponent name="query"  class="org.apache.solr.handler.component.AliasingQueryComponent" />


### Alias configuration file

The alias handler expects a query_aliases.xml file to be  the Solr core's conf directory. If the file is not present the handler will throw an exception.

Example of query_aliases.xml:  

    <alias-configs>
        <alias-config>
            <alias-pseudofield>collection</alias-pseudofield>
            <alias-defs>
                <alias-def>
                    <alias>fashion</alias>
                    <query>(PROVIDER:"Europeana Fashion") AND NOT(proxy_dc_identifier:"01457L") AND NOT(proxy_dcterms_created:[0001 TO 1300]) OR NOT(proxy_dcterms_created:[2018 TO 9999]) OR NOT(YEAR:[2018 TO 9999])</query> 
                </alias-def>
            </alias-defs>
        </alias-config>
    </alias-configs>

## To Do

The JUnit testing is basic. The tests should use more realistic data and test all possible types of query.

Currently the alias configuration is read once for each core, the first time the Handler receives a request from that core. It might be good to include the possibility to request the handler to re-read the configuration file which would enable the configuration to be updated without having to restart the core.
