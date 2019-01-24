package org.apache.solr.handler.component;

import org.apache.solr.request.SolrQueryRequest;
import org.apache.solr.response.SolrQueryResponse;
import org.apache.solr.common.util.NamedList;


/**
 * Expands aliases into queries for thematic collections.
 *
 * Operates by taking apart the passed request, scanning it for thematic-collection keywords,
 * and replacing those it finds with the appropriate expanded query.
 *
 * @author thill
 * @author n.ireson@sheffield.ac.uk
 * @version 2018.07.28
 */
public class AliasingSearchHandler
        extends SearchHandler {

    public void init(NamedList params) {
        super.init(params);
    }

    @Override
    public void handleRequestBody(SolrQueryRequest req, SolrQueryResponse rsp)
            throws Exception {
        QueryAliasing.modifyRequest(req);
        super.handleRequestBody(req, rsp);
    }

    @Override
    public String getDescription() {
        return "Expands keyword arguments and pseudofields into Solr-parseable queries";
    }
}