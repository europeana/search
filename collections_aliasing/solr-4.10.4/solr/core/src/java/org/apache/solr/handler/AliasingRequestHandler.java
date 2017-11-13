package org.apache.solr.handler;

import java.util.HashMap;
import java.util.List;
import org.apache.solr.handler.RequestHandlerBase;
import org.apache.solr.request.SolrQueryRequest;
import org.apache.solr.response.SolrQueryResponse;
import org.apache.solr.common.util.NamedList;
import org.apache.solr.core.AliasConfig;

public class AliasingRequestHandler extends RequestHandlerBase{
     

  public void init(NamedList params) {
    
      super.init(params);
    
  }
  
  @Override
  public void handleRequestBody(SolrQueryRequest req, SolrQueryResponse rsp)
      throws Exception {
    
    AliasConfig aliasConfig = req.getCore().getAliasConfig();
    HashMap<String, HashMap<String, String>> aliases = aliasConfig.getAliases();
    // so now we need to check whether the 'fq' parameter holds any of the aliased fields
    // for the moment we just return the query that's associated with that alias
    rsp.add("test", aliases.toString());
    
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