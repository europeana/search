package europeana.search.testing;

import java.io.IOException;
import java.io.InputStream;
import java.net.URL;
import java.nio.file.Paths;
import java.util.Collection;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Properties;

import org.apache.log4j.Logger;
import org.apache.log4j.PropertyConfigurator;
import org.apache.solr.client.solrj.SolrClient;
import org.apache.solr.client.solrj.SolrQuery;
import org.apache.solr.client.solrj.SolrQuery.ORDER;
import org.apache.solr.client.solrj.SolrServerException;
import org.apache.solr.client.solrj.impl.HttpSolrClient;
import org.apache.solr.client.solrj.response.QueryResponse;
import org.apache.solr.common.SolrDocument;
import org.apache.solr.common.SolrInputDocument;
import org.apache.solr.common.params.CommonParams;
import org.apache.solr.common.params.CursorMarkParams;
import org.apache.solr.common.util.SimpleOrderedMap;

import europeana.utils.Buffer;
import europeana.utils.SolrErrorHandling;
import europeana.utils.Utils;

public class Process {
	
	static Logger logger = Logger.getLogger(Process.class);
	static final Integer ROWS = 500;
	
	private static boolean CheckFields(SolrDocument sourceDoc, SolrDocument targetDoc) {
		Boolean chck = true;
		chck = chck && targetDoc.getFieldNames().containsAll(sourceDoc.getFieldNames());
		chck = chck && sourceDoc.getFieldNames().containsAll(targetDoc.getFieldNames());
		if (!chck) {
			logger.error("Record " +  targetDoc.getFieldValue("europeana_id") + " does not correspond to original metadata");
			return false;
		}
		return true;
	}
	
	private static boolean CheckContent(SolrDocument sourceDoc, SolrDocument targetDoc) {
		Boolean chck = true;
		for (String f: sourceDoc.getFieldNames()) {
			if (!f.equalsIgnoreCase("_version_") && !f.equalsIgnoreCase("timestamp")) {
				Collection<Object> targetvalues = targetDoc.getFieldValues(f);
				Collection<Object> sourcevalues = sourceDoc.getFieldValues(f);
				chck = chck && targetvalues.containsAll(sourcevalues);
				chck = chck && sourcevalues.containsAll(targetvalues);
			}
		}
		if (!chck) {
			logger.error("Record " +  targetDoc.getFieldValue("europeana_id") + " does not correspond to original metadata");
			return false;
		}
		return true;
	}
	
	private static void Validate(SolrClient targetClient, SolrClient sourceClient) throws SolrServerException, IOException, InterruptedException {
		logger.info("Starting validation");
		SolrQuery query = new SolrQuery();
		query.setQuery("*:*");
		query.setRows(ROWS);
	    query.addSort("europeana_id", ORDER.asc);
	    
	    
	    String cursorMark = CursorMarkParams.CURSOR_MARK_START;
	    boolean done = false;
	    int count = 0;
	    while (!done) {
	        query.set(CursorMarkParams.CURSOR_MARK_PARAM, cursorMark);
	        QueryResponse rsp = SolrErrorHandling.Query(targetClient, query);
	        String nextCursorMark = rsp.getNextCursorMark();
	        
	        for (SolrDocument targetDoc : rsp.getResults()) {
	    		SolrQuery querySource = new SolrQuery();
	    		String europeana_id = targetDoc.getFieldValue("europeana_id").toString();
	    		querySource.setQuery("europeana_id"+":"+"\""+ europeana_id + "\"");
	    		QueryResponse sourceResponse = SolrErrorHandling.Query(sourceClient, querySource);
	    		SolrDocument sourceDoc = sourceResponse.getResults().get(0);
	    		CheckFields(sourceDoc, targetDoc);
	    		CheckContent(sourceDoc, targetDoc);
				count++;
				logger.info("Validated " + count + " records");

			}
	        if (cursorMark.equals(nextCursorMark)) {
	            done = true;
	        }
	        cursorMark = nextCursorMark;
	    }

	    logger.info("Validation completed: "+ count + " records checked");
	}
	
	public static void main(String[] args) throws Exception {
		try {
			InputStream is = Process.class.getClassLoader().getResourceAsStream("resources/log4j.properties");
			PropertyConfigurator.configure(is);
					
			Properties p;
			p = Utils.readProperties(Process.class.getClassLoader().getResourceAsStream("resources/config.properties"));
		
			URL sourceClientURL =  new URL(p.getProperty("source"));
			SolrClient sourceClient = new HttpSolrClient.Builder(sourceClientURL.toString()).build();
			URL targetClientURL = new URL(p.getProperty("target"));
			SolrClient targetClient = new HttpSolrClient.Builder(targetClientURL.toString()).build();
			Validate(targetClient, sourceClient);
		} catch (Exception e) {
			logger.fatal("Fatal error" + e.getMessage());
			e.printStackTrace();
			throw e;
		}
	}

}
