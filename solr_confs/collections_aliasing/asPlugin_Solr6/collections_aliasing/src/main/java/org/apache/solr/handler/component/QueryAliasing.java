package org.apache.solr.handler.component;

import org.apache.solr.common.SolrException;
import org.apache.solr.common.params.MultiMapSolrParams;
import org.apache.solr.common.params.SolrParams;
import org.apache.solr.core.AliasConfig;
import org.apache.solr.core.SolrCore;
import org.apache.solr.request.SolrQueryRequest;

import java.nio.file.Path;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class QueryAliasing {

  private static final Logger LOGGER = LoggerFactory.getLogger(QueryAliasing.class);
  // It is possible for the map to be accessed by different thread, thus use ConcurrentHashMap.
  private static final Map<SolrCore, AliasConfig> coreAliasConfigMap = new ConcurrentHashMap<>();

  static void modifyRequest(SolrQueryRequest request) {
    AliasConfig aliasConfig = getAliasConfig(request);
    SolrParams params = request.getParams();
    Iterator<String> pnit = params.getParameterNamesIterator();
    Map<String, String[]> modifiedParams = new HashMap<>();
    while (pnit.hasNext()) {
      String pname = pnit.next();
      String[] pvalues = params.getParams(pname);
      if (!pname.equals("q") && !pname.equals("fq")) {
        modifiedParams.put(pname, pvalues);
      } else {
        String[] modifiedValues = QueryAliasing.modifyValues(aliasConfig, pvalues);
        modifiedParams.put(pname, modifiedValues);
      }
    }
    MultiMapSolrParams newParams = new MultiMapSolrParams(modifiedParams);
    request.setParams(newParams);
  }

  private static AliasConfig getAliasConfig(SolrQueryRequest req) {
    SolrCore core = req.getCore();
    AliasConfig aliasConfig = coreAliasConfigMap.get(core);
    if (aliasConfig == null) {
      try {
        //First try to load resource with the default loader
        System.out.println("test");
        aliasConfig = new AliasConfig(core.getResourceLoader(), AliasConfig.DEFAULT_CONF_FILE, null);
      } catch (Exception exception) {
        LOGGER.warn("Could not find file in default resource loader. Will try core directory now.", exception);
        try {
          // Note it is possible to use the init param to parameterise the AliasConfig constructor
          Path instanceDir = core.getCoreDescriptor().getInstanceDir();
          Path confDir = instanceDir.resolve("conf");
          aliasConfig = new AliasConfig(confDir, AliasConfig.DEFAULT_CONF_FILE, null);
        } catch (Exception e) {
          throw new SolrException(SolrException.ErrorCode.NOT_FOUND, "Alias config file not found", e);
        }
      }
      coreAliasConfigMap.put(core, aliasConfig);
    }
    return aliasConfig;
  }

  /*
   * Given a HashMap listing pseudofields and their appropriate aliases and expansions,
   * scans the passed list of parameters for pseudofields and swaps in expanded queries as
   * appropriate.
   *
   * @author thill
   * @version 2017.11.14
   */
  private static String[] modifyValues(AliasConfig aliasConfig, String[] checkValues) {

    HashMap<String, HashMap<String, String>> aliases = aliasConfig.getAliases();
    String[] modifiedValues = new String[checkValues.length];
    for (int i = 0; i < checkValues.length; i++) {
      // first, check if this is a fielded search
      String checkValue = checkValues[i];
      if (checkValue.contains(":")) {
        for (String psField : aliases.keySet()) {
          if (checkValue.contains(psField + ":")) {
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
              String warning = "Collection \"" + illegalField + "\" is not well-formed; "
                  + "aliases may contain only alphanumberic characters and the \"_\" character.";
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
              } else {
                String msg = "Collection \"" + collectionName + "\" not defined in " + aliasConfig.getConfigFilename();
                throw new SolrException(SolrException.ErrorCode.NOT_FOUND, msg);
              }
            }
          }
        }
      }
      modifiedValues[i] = checkValue;
    }

    return modifiedValues;
  }
}
