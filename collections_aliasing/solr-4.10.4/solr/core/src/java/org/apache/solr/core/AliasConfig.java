package org.apache.solr.core;

import java.io.IOException;
import java.util.HashMap;
import javax.xml.parsers.ParserConfigurationException;
import javax.xml.xpath.XPathConstants;
import org.apache.solr.cloud.ZkSolrResourceLoader;
import org.apache.solr.common.SolrException;
import org.apache.solr.common.SolrException.ErrorCode;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.w3c.dom.NodeList;
import org.xml.sax.InputSource;
import org.xml.sax.SAXException;
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

public class AliasConfig extends Config {
  
  public static final Logger log = LoggerFactory.getLogger(SolrConfig.class);
  public static final String DEFAULT_CONF_FILE = "query_aliases.xml"; 
  public final HashMap<String, HashMap<String, String>> aliases;
  
  /** Creates a default instance from query_aliases.xml. */
  public AliasConfig()
  throws ParserConfigurationException, IOException, SAXException {
    this( (SolrResourceLoader) null, DEFAULT_CONF_FILE, null );
  }
  
  /** Creates a configuration instance from a configuration name.
   * A default resource loader will be created (@see SolrResourceLoader)
   *@param name the configuration name used by the loader
   */
  public AliasConfig(String name)
  throws ParserConfigurationException, IOException, SAXException {
    this( (SolrResourceLoader) null, name, null);
  }

  /** Creates a configuration instance from a configuration name and stream.
   * A default resource loader will be created (@see SolrResourceLoader).
   * If the stream is null, the resource loader will open the configuration stream.
   * If the stream is not null, no attempt to load the resource will occur (the name is not used).
   *@param name the configuration name
   *@param is the configuration stream
   */
  public AliasConfig(String name, InputSource is)
  throws ParserConfigurationException, IOException, SAXException {
    this( (SolrResourceLoader) null, name, is );
  }
  
  /** Creates a configuration instance from an instance directory, configuration name and stream.
   *@param instanceDir the directory used to create the resource loader
   *@param name the configuration name used by the loader if the stream is null
   *@param is the configuration stream 
   */
  public AliasConfig(String instanceDir, String name, InputSource is)
  throws ParserConfigurationException, IOException, SAXException {
    this(new SolrResourceLoader(instanceDir), name, is);
  }
  
  
  public AliasConfig(SolrResourceLoader loader, String name, InputSource is)
      throws ParserConfigurationException, IOException, SAXException {
    
      super(loader, name, is, "/alias-configs/");
      this.aliases = populateAliases();
      Config.log.info("Loaded Aliases Config: " + name);
  
  }
  
  private HashMap<String, HashMap<String, String>> populateAliases() {
    
    HashMap<String,HashMap<String, String>> tempAliases = new HashMap<String, HashMap<String, String>>();
    NodeList aliasFields = (NodeList) evaluate(".", XPathConstants.NODESET);
    for(int i = 0; i < aliasFields.getLength(); i++) {
      
      String fieldName = get("alias-pseudofield");
      NodeList aliasNodes = (NodeList) evaluate(".", XPathConstants.NODESET);
      HashMap<String, String> aliasMap = new HashMap<String, String>();
      for(int j = 0; j < aliasNodes.getLength(); j++) {
        
        String alias = get("alias");
        String query = get("query");
        aliasMap.put(alias, query);
        
      }
      tempAliases.put(fieldName, aliasMap);
    }

    return tempAliases;
    
  }
  
  public static AliasConfig readFromResourceLoader(SolrResourceLoader loader, String name) {
    try {
      return new AliasConfig(loader, name, null);
    }
    catch (Exception e) {
      String resource;
      if (loader instanceof ZkSolrResourceLoader) {
        resource = name;
      } else {
        resource = loader.getConfigDir() + name;
      }
      throw new SolrException(ErrorCode.SERVER_ERROR, "Error loading aliasing config from " + resource, e);
    }
  }
  
}
