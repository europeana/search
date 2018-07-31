/*
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package org.apache.solr.handler.component;

import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.apache.solr.common.SolrException;
import org.apache.solr.common.params.MultiMapSolrParams;
import org.apache.solr.common.params.SolrParams;
import org.apache.solr.common.util.NamedList;
import org.apache.solr.core.AliasConfig;
import org.apache.solr.request.SolrQueryRequest;
import org.apache.solr.response.SolrQueryResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class AliasingRequestHandler extends SearchHandler {
  // in a fashion suitable to this subclass as well
  private static final Logger logger = LoggerFactory.getLogger(AliasingRequestHandler.class.getSimpleName());

  public void init(NamedList params) {

    super.init(params);

  }

  /**
   * Expands aliases into queries for thematic collections.
   * <p>
   * Operates by taking apart the passed request, scanning it for thematic-collection keywords,
   * and replacing those it finds with the appropriate expanded query.
   *
   * @author thill
   * @version 2017.11.14
   */

  @Override
  public void handleRequestBody(SolrQueryRequest req, SolrQueryResponse rsp)
      throws Exception {
    logger.debug("AliasingRequestHandler is handling ... ");

    AliasConfig aliasConfig = req.getCore().getAliasConfig();
    HashMap<String, HashMap<String, String>> aliases = aliasConfig.getAliases();
    SolrParams params = req.getParams();
    Iterator<String> pnit = params.getParameterNamesIterator();
    Map<String, String[]> modifiedParams = new HashMap<String, String[]>();
    //String paramnames = "";
    while (pnit.hasNext()) {

      String pname = pnit.next();
      //paramnames += pname + " ";
      String[] pvalues = params.getParams(pname);
      if (!pname.equals("q") && !pname.equals("fq")) {

        modifiedParams.put(pname, pvalues);

      } else {
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
    for (int i = 0; i < checkValues.length; i++) {
      // first, check if this is a fielded search
      String checkValue = checkValues[i];
      if (checkValue.contains(":")) {

        for (String psField : aliases.keySet()) {

          if (checkValue.contains(psField + ":")) {
            logger.debug(String.format("modify query [%s] with matched [%s] alias", checkValue, psField));

            Pattern p = Pattern.compile("\\b" + psField + ":([\\w]+)\\b");
            Matcher m = p.matcher(checkValue);
            m.reset();
            if (!m.find()) {

              String[] fieldBits = checkValue.split(psField + ":");
              String illegalField = "[Empty Field]";
              if (fieldBits.length > 1) {

                illegalField = fieldBits[1];
                String[] illegalFieldBits = illegalField.split("\\s");
                illegalField = illegalFieldBits[0];

              }
              String warning = "Collection \"" + illegalField + "\" is not well-formed; aliases may contain only alphanumberic characters and the \"_\" character.";
              throw new SolrException(SolrException.ErrorCode.NOT_FOUND, warning);

            }
            m.reset();
            while (m.find()) {

              String all = checkValue.substring(m.start(), m.end());
              String[] bits = all.split(":");
              String collectionName = bits[1];
              HashMap<String, String> themeAliases = aliases.get(psField);
              if (themeAliases.containsKey(collectionName)) {
                String fullQuery = themeAliases.get(collectionName);
                checkValue = checkValue.replaceAll("\\b" + psField + ":" + collectionName + "\\b", fullQuery);

                logger.debug(String.format("modify query [%s] in [%s] alias collection field to [%s]", checkValue, psField, checkValue));
              } else {

                String msg = "Collection \"" + collectionName + "\" not defined in query_aliases.xml";
                throw new SolrException(SolrException.ErrorCode.NOT_FOUND, msg);

              }

            }

          }

        }

      }
      modifiedValues[i] = checkValue;
    }
    // if it *is* fielded, does it contain any of the pseudofield fields?


    // now we attempt a regex


    // check to make sure this is a fielded search
    // (i) does it contain a semicolon?
    /**

     String fieldName = checkValue.split(":")[0].trim();
     // (ii) is the semicolon not part of a search term (such as a URI)?
     if(!fieldName.contains("\"") && !fieldName.contains("'")) {
     // if so, expand
     if(aliases.containsKey(fieldName)) {
     HashMap<String, String> themeAliases = aliases.get(fieldName);
     String collectionName = checkValue.split(":")[1].trim();
     // let's also eliminate any possible confusion as to whether this is a phrase query or not
     collectionName = collectionName.replace("\"", "");
     collectionName = collectionName.replace("'", "");
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

     }*/

    return modifiedValues;
  }

  private String outputParams(SolrParams params) {

    // for debugging purposes

    StringBuilder sb = new StringBuilder();
    Iterator<String> pit = params.getParameterNamesIterator();

    while (pit.hasNext()) {

      String pname = pit.next();
      sb.append(pname);
      sb.append(" :");
      String[] pvalues = params.getParams(pname);
      for (int i = 0; i < pvalues.length; i++) {

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