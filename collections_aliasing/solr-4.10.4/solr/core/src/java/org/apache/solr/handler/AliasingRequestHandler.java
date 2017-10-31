package org.apache.solr.handler;

import org.apache.solr.handler.RequestHandlerBase;
import org.apache.solr.request.SolrQueryRequest;
import org.apache.solr.response.SolrQueryResponse;

public class AliasingRequestHandler extends RequestHandlerBase{

  @Override
  public void handleRequestBody(SolrQueryRequest req, SolrQueryResponse rsp)
      throws Exception {
    
    String test = req.getParams().get("test", "Success");
    rsp.add("test", "Test " + test);
    
    
  }

  @Override
  public String getDescription() {
    String desc = "Expands keyword arguments and pseudofields into Solr-parseable queries";
    return desc;
  }

  @Override
  public String getSource() {
    return null;
  }
  

}