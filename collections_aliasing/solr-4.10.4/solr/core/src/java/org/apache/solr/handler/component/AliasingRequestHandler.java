package org.apache.solr.handler.component;

import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import org.apache.solr.request.SolrQueryRequest;
import org.apache.solr.response.SolrQueryResponse;
import org.apache.solr.common.SolrException;
import org.apache.solr.common.params.MultiMapSolrParams;
import org.apache.solr.common.params.SolrParams;
import org.apache.solr.common.util.NamedList;
import org.apache.solr.core.AliasConfig;

public class AliasingRequestHandler extends SearchHandler{
     // TODO: check that the interfaces implemented in SearchHandler are done so
     // in a fashion suitable to this subclass as well

  public void init(NamedList params) {
    
      super.init(params);
    
  }
  
  /**
   * Expands aliases into queries for thematic collections.
   * 
   * Operates by taking apart the passed request, scanning it for thematic-collection keywords,
   * and replacing those it finds with the appropriate expanded query.
   * 
   * @author thill
   * @version 2017.11.14
   */
  
  @Override
  public void handleRequestBody(SolrQueryRequest req, SolrQueryResponse rsp)
      throws Exception {
    
    AliasConfig aliasConfig = req.getCore().getAliasConfig();
    HashMap<String, HashMap<String, String>> aliases = aliasConfig.getAliases();
    SolrParams params = req.getParams();
    Iterator<String> pnit = params.getParameterNamesIterator();
    Map<String, String[]> modifiedParams = new HashMap<String, String[]>();
    String paramnames = "";
    while(pnit.hasNext()) {
      
      String pname = pnit.next();
      paramnames += pname + " ";
      String[] pvalues = params.getParams(pname);
      if(!pname.equals("q") && !pname.equals("fq")) {
        
        modifiedParams.put(pname, pvalues);
        
      }
      else {
        String[] modifiedValues = this.modifyValues(aliases, pvalues);
        modifiedParams.put(pname, modifiedValues);
      
      }
      
    }
    MultiMapSolrParams newParams = new MultiMapSolrParams(modifiedParams);
    req.setParams(newParams);
    // a little debugging check
    //String paramCheck = outputParams(newParams);
    // rsp.add("test", paramCheck);
    super.handleRequestBody(req, rsp);
    
  }
  
  /*
   * Given a HashMap listing pseudofields and their appropriate aliases and expansions, 
   * scans the passed list of parameters for pseudofields and swaps in expanded queries as
   * appropriate.
   * 
   * @author thill
   * @version 2017.11.14
   */
  
  private String[] modifyValues(HashMap<String, HashMap<String, String>> aliases, String[] checkValues) throws Exception {
    
    String[] modifiedValues = new String[checkValues.length];
    for(int i = 0; i < checkValues.length; i++) {
      // check to make sure this is a fielded search
      // (i) does it contain a semicolon?
      String checkValue = checkValues[i];
      if(checkValue.contains(":")) {

        String fieldName = checkValue.split(":")[0].trim();
        // (ii) is the semicolon not part of a search term (such as a URI)?
        if(!fieldName.contains("\"") && !fieldName.contains("'")) {
          // if so, expand
          if(aliases.containsKey(fieldName)) {
            HashMap<String, String> themeAliases = aliases.get(fieldName);
            String collectionName = checkValue.split(":")[1].trim();
            if(themeAliases.containsKey(collectionName)) {
              checkValue = themeAliases.get(collectionName);
            }
            else {
              
              String msg = "Collection \"" + collectionName + "\" not defined in query_aliases.xml";
              throw new SolrException(SolrException.ErrorCode.NOT_FOUND, msg);
              
            }

          }
          
        }
        
      }    
      modifiedValues[i] = checkValue;      
    }
    
    return modifiedValues;
  }
  
  private String outputParams(SolrParams params) {
    
    // for debugging purposes
    
    StringBuilder sb = new StringBuilder();
    Iterator<String> pit = params.getParameterNamesIterator();
    
    while(pit.hasNext()) {
      
      String pname = pit.next();
      sb.append(pname);
      sb.append(" :");
      String[] pvalues = params.getParams(pname);
      for(int i = 0; i < pvalues.length; i++) {
        
        sb.append(pvalues[i]);
        sb.append(" ");
        
      }
      sb.append("\n\n");
      
    }
    
    return sb.toString();
    
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