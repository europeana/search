package org.apache.solr.handler.component;

import java.io.IOException;
import org.apache.solr.common.params.SolrParams;

public class AliasingQueryComponent
        extends QueryComponent {

    @Override
    public void process(ResponseBuilder rb)
            throws IOException {
        SolrParams params = rb.req.getParams();
        if (!params.getBool(COMPONENT_NAME, true)) {
            return;
        }
        QueryAliasing.modifyRequest(rb.req);

        super.process(rb);
    }
}
