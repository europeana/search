package org.apache.solr.core;

//import com.sun.org.apache.xerces.internal.dom.ElementImpl;
import org.w3c.dom.Element;
import org.apache.solr.cloud.ZkSolrResourceLoader;
import org.apache.solr.common.SolrException;
import org.apache.solr.core.SolrConfig;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.w3c.dom.NodeList;

import org.xml.sax.InputSource;
import org.xml.sax.SAXException;

import javax.swing.text.Document;
import javax.xml.parsers.ParserConfigurationException;
import javax.xml.xpath.XPathConstants;
import javax.xml.xpath.XPathExpression;
import java.io.IOException;
import java.lang.invoke.MethodHandles;
import java.nio.file.Path;
import java.util.HashMap;

/**
 * This class is a remnant form when the configuration was loaded as part of the initial Solr configuration.
 * However that involved changing and recompiling the whole Solr cadebase. Now the configuration for each core
 * is stored in a static map and read when the first AliasingSearchHandler is initialised
 *
 * @author thill
 * @author n.ireson@sheffield.ac.uk
 * @version 2018.07.28
 */
public class AliasConfig
        extends SolrConfig {

    private static final Logger log = LoggerFactory.getLogger(MethodHandles.lookup().lookupClass());
    public static final String DEFAULT_CONF_FILE = "query_aliases.xml";
    private final String configFilename;
    private final HashMap<String, HashMap<String, String>> aliases;


/**
     * Creates a default instance from query_aliases.xml.
     */

    public AliasConfig()
            throws ParserConfigurationException, IOException, SAXException {
        this(DEFAULT_CONF_FILE);
    }


/**
     * Creates a configuration instance from a configuration name.
     * A default resource loader will be created (@see SolrResourceLoader)
     *
     * @param name the configuration name used by the loader
     */

    public AliasConfig(String name)
            throws ParserConfigurationException, IOException, SAXException {
        this((SolrResourceLoader) null, name, null);
    }


/**
     * Creates a configuration instance from a configuration name and stream.
     * A default resource loader will be created (@see SolrResourceLoader).
     * If the stream is null, the resource loader will open the configuration stream.
     * If the stream is not null, no attempt to load the resource will occur (the name is not used).
     *
     * @param name the configuration name
     * @param is   the configuration stream
     */

    public AliasConfig(String name, InputSource is)
            throws ParserConfigurationException, IOException, SAXException {
        this((SolrResourceLoader) null, name, is);
    }


/**
     * Creates a configuration instance from an instance directory, configuration name and stream.
     *
     * @param instanceDir the directory used to create the resource loader
     * @param name        the configuration name used by the loader if the stream is null
     * @param is          the configuration stream
     */

    public AliasConfig(Path instanceDir, String name, InputSource is)
            throws ParserConfigurationException, IOException, SAXException {
        this(new SolrResourceLoader(instanceDir), name, is);
    }


    public AliasConfig(SolrResourceLoader loader, String name, InputSource is)
            throws ParserConfigurationException, IOException, SAXException {

        super(loader, name, is, "/alias-configs/");
        this.aliases = populateAliases();
        log.info("Loaded Aliases Config: " + name);
        configFilename = name;
    }

    public String getConfigFilename() { return configFilename; }

    private HashMap<String, HashMap<String, String>> populateAliases() {

        HashMap<String, HashMap<String, String>> allAliases = new HashMap<>();

        NodeList aliasFields = (NodeList) evaluate("alias-config", XPathConstants.NODESET);
        System.out.println("Processing alias");
        for (int i = 0; i < aliasFields.getLength(); i++) {
            Element pseudofieldNode = (Element) aliasFields.item(i);
            String fieldName = pseudofieldNode.getElementsByTagName("alias-pseudofield").item(0).getTextContent();
            System.out.println("Field name:"+ fieldName);
            NodeList configs = pseudofieldNode.getElementsByTagName("alias-def");
            
            HashMap<String, String> aliasMap = new HashMap<>();
            for (int j = 0; j < configs.getLength(); j++) {
                Element configNode = (Element) configs.item(j);
                String alias = configNode.getElementsByTagName("alias").item(0).getTextContent();
                System.out.println("Alias:"+alias);
                String query = configNode.getElementsByTagName("query").item(0).getTextContent();
                System.out.println("Query:"+query);
                aliasMap.put(alias, query);
            }
            allAliases.put(fieldName, aliasMap);
        }

        return allAliases;
    }

    public HashMap<String, HashMap<String, String>> getAliases() {
        return aliases;
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
            throw new SolrException(SolrException.ErrorCode.SERVER_ERROR,
                    "Error loading aliasing config from " + resource, e);
        }
    }

}