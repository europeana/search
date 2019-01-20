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

import java.io.File;
import java.io.IOException;
import java.lang.invoke.MethodHandles;
import java.nio.file.Files;
import java.util.ArrayList;
import java.util.List;
import java.util.Properties;

import com.carrotsearch.randomizedtesting.annotations.ThreadLeakFilters;
import org.apache.commons.io.FileUtils;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.lucene.util.IOUtils;
import org.apache.lucene.util.LuceneTestCase.Slow;
import org.apache.lucene.util.QuickPatchThreadsFilter;
import org.apache.solr.SolrIgnoredThreadsFilter;
import org.apache.solr.SolrTestCaseJ4;
import org.apache.solr.client.solrj.SolrQuery;
import org.apache.solr.client.solrj.SolrServerException;
import org.apache.solr.client.solrj.embedded.JettyConfig;
import org.apache.solr.client.solrj.embedded.JettySolrRunner;
import org.apache.solr.client.solrj.impl.HttpClientUtil;
import org.apache.solr.client.solrj.impl.HttpSolrClient;
import org.apache.solr.client.solrj.response.QueryResponse;
import org.apache.solr.client.solrj.response.SolrResponseBase;
import org.apache.solr.common.SolrInputDocument;
import org.apache.solr.core.AliasConfig;
import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;


/**
 * Test for AliasingSearchHandlerHttpSolrClientTest
 *
 * @since solr 1.4
 */
@Slow
@ThreadLeakFilters(defaultFilters = true, filters = {
        SolrIgnoredThreadsFilter.class,
        QuickPatchThreadsFilter.class
})
public class AliasingSearchHandlerHttpSolrClientTest
        extends SolrTestCaseJ4 {

    private static final Logger log = LoggerFactory.getLogger(MethodHandles.lookup().lookupClass());

    private SolrInstance solr;
    private CloseableHttpClient httpClient;

    // TODO: fix this test to not require FSDirectory
    private static String savedFactory;

    @BeforeClass
    public static void beforeClass() {
        savedFactory = System.getProperty("solr.DirectoryFactory");
        System.setProperty("solr.directoryFactory", "org.apache.solr.core.MockFSDirectoryFactory");
        System.setProperty("tests.shardhandler.randomSeed", Long.toString(random().nextLong()));
        System.setProperty("solr.tests.IntegerFieldType", "org.apache.solr.schema.TrieIntField");
        System.setProperty("solr.tests.LongFieldType", "org.apache.solr.schema.TrieLongField");
        System.setProperty("solr.tests.FloatFieldType", "org.apache.solr.schema.TrieFloatField");
        System.setProperty("solr.tests.DoubleFieldType", "org.apache.solr.schema.TrieDoubleField");
        System.setProperty("solr.tests.DateFieldType", "org.apache.solr.schema.TrieDateField");
        System.setProperty("solr.tests.numeric.dv", "true");
    }

    @AfterClass
    public static void afterClass() {
        if (savedFactory == null) {
            System.clearProperty("solr.directoryFactory");
        } else {
            System.setProperty("solr.directoryFactory", savedFactory);
        }
        System.clearProperty("tests.shardhandler.randomSeed");
    }

    @Override
    public void setUp()
            throws Exception {
        super.setUp();
        httpClient = HttpClientUtil.createClient(null);
        HttpClientUtil.setConnectionTimeout(httpClient, 1000);
        solr = new SolrInstance("solr/collection1", createTempDir("instance").toFile(), 0);
        solr.setUp();
        solr.startJetty();
        addDocs(solr);
    }

    private void addDocs(SolrInstance solrInstance)
            throws IOException, SolrServerException {
        List<SolrInputDocument> docs = new ArrayList<>();
        for (int i = 0; i < 10; i++) {
            SolrInputDocument doc = new SolrInputDocument();
            doc.addField("id", i);
            doc.addField("name", solrInstance.name);
            docs.add(doc);
        }
        SolrResponseBase resp;
        try (HttpSolrClient client = getHttpSolrClient(solrInstance.getUrl(), httpClient)) {
            resp = client.add(docs);
            assertEquals(0, resp.getStatus());
            resp = client.commit();
            assertEquals(0, resp.getStatus());
        }
    }

    @Override
    public void tearDown()
            throws Exception {
        if (solr != null) {
            solr.tearDown();
        }
        httpClient.close();
        super.tearDown();
    }

    public void testSimple()
            throws Exception {
        HttpSolrClient client = getHttpSolrClient(solr.getUrl(), httpClient);
        SolrQuery solrQuery = new SolrQuery("*:*");
        // todo test complex querying with and without aliasing
        QueryResponse resp = client.query(solrQuery);
        assertEquals(10, resp.getResults().getNumFound());
    }

    private static class SolrInstance {
        String name;
        File homeDir;
        File dataDir;
        File confDir;
        int port;
        JettySolrRunner jetty;

        public SolrInstance(String name, File homeDir, int port) {
            this.name = name;
            this.homeDir = homeDir;
            this.port = port;

            dataDir = new File(homeDir + "/collection1", "data");
            confDir = new File(homeDir + "/collection1", "conf");
        }

        public String getHomeDir() {
            return homeDir.toString();
        }

        public String getUrl() {
            return buildUrl(port, "/solr/collection1");
        }

        public String getSchemaFile() {
            return "solrj/solr/collection1/conf/schema-replication1.xml";
        }

        public String getConfDir() {
            return confDir.toString();
        }

        public String getDataDir() {
            return dataDir.toString();
        }

        public String getSolrConfigFile() {
            return "solrj/solr/collection1/conf/solrconfig-slave1.xml";
        }

        public String getSolrXmlFile() {
            return "solrj/solr/solr.xml";
        }


        public void setUp()
                throws Exception {
            homeDir.mkdirs();
            dataDir.mkdirs();
            confDir.mkdirs();

            FileUtils.copyFile(SolrTestCaseJ4.getFile(getSolrXmlFile()), new File(homeDir, "solr.xml"));

            File f = new File(confDir, "solrconfig.xml");
            FileUtils.copyFile(SolrTestCaseJ4.getFile(getSolrConfigFile()), f);
            f = new File(confDir, "schema.xml");
            FileUtils.copyFile(SolrTestCaseJ4.getFile(getSchemaFile()), f);
            f = new File(confDir, AliasConfig.DEFAULT_CONF_FILE);
            FileUtils.copyFile(SolrTestCaseJ4.getFile(getSchemaFile()), f);

            Files.createFile(homeDir.toPath().resolve("collection1/core.properties"));
        }

        public void tearDown()
                throws Exception {
            if (jetty != null) {
                jetty.stop();
            }
            log.info("Removing temporary Solr home: {}", homeDir.toPath());
            IOUtils.rm(homeDir.toPath());
        }

        public void startJetty()
                throws Exception {

            Properties props = new Properties();
            props.setProperty("solrconfig", "bad_solrconfig.xml");
            props.setProperty("solr.data.dir", getDataDir());

            JettyConfig jettyConfig = JettyConfig.builder(buildJettyConfig("/solr")).setPort(port).build();

            jetty = new JettySolrRunner(getHomeDir(), props, jettyConfig);
            jetty.start();
            int newPort = jetty.getLocalPort();
            if (port != 0 && newPort != port) {
                fail("TESTING FAILURE: could not grab requested port.");
            }
            this.port = newPort;
//      System.out.println("waiting.........");
//      Thread.sleep(5000);
        }
    }
}
