package europeana.search.indexing;

import java.io.IOException;
import java.io.InputStream;
import java.net.URL;
import java.nio.file.Paths;
import java.util.HashSet;
import java.util.List;
import java.util.Properties;

import org.apache.log4j.Logger;
import org.apache.log4j.PropertyConfigurator;
import org.apache.solr.client.solrj.SolrClient;
import org.apache.solr.client.solrj.SolrQuery;
import org.apache.solr.client.solrj.SolrQuery.ORDER;
import org.apache.solr.client.solrj.SolrServerException;
import org.apache.solr.client.solrj.impl.CloudSolrClient;
import org.apache.solr.client.solrj.impl.ConcurrentUpdateSolrClient;
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
	
	
	private static SolrInputDocument GetDocument(SolrDocument document, HashSet<String> nvfields) {
		SolrInputDocument outputDoc = new SolrInputDocument();
		document.forEach(p -> {
			if (!outputDoc.containsKey(p.getKey())) {
				if (!nvfields.contains(p.getKey().toString())){
						outputDoc.addField(p.getKey(), p.getValue());
				}
			}
		});
		outputDoc.setField("_version_", 0);
		return outputDoc;
	}
	
	private static void Index(SolrClient sourceClient, SolrClient targetClient, Integer buffersize, HashSet<String> nvfields, Integer records) throws SolrServerException, IOException {
		Buffer<SolrInputDocument> buffer = new Buffer<SolrInputDocument>(buffersize);
		SolrQuery query = new SolrQuery();
		query.setQuery("*:*");
		query.setStart(0);
	    query.setRows(ROWS);
	    query.addSort("europeana_id", ORDER.asc);
	    
	    String cursorMark = CursorMarkParams.CURSOR_MARK_START;
	    boolean done = false;
	    while (!done && records > 0) {
	        query.set(CursorMarkParams.CURSOR_MARK_PARAM, cursorMark);
	        QueryResponse rsp = SolrErrorHandling.Query(sourceClient, query);
	        String nextCursorMark = rsp.getNextCursorMark();
	        for (SolrDocument d : rsp.getResults()) {
	        	SolrInputDocument toIndex = GetDocument(d, nvfields);
				buffer.Add(toIndex);
				records--;
				if (buffer.isFull()) {
					List<SolrInputDocument> toindex = buffer.Retrieve();
					if (!toindex.isEmpty()) {
						targetClient.add(toindex);
						logger.info(" - batch "+ buffer.GetItemsBuffered() / buffer.GetCapacity() + " - Total documents indexed: " + buffer.GetItemsBuffered());
					}
				}
			}
	        if (cursorMark.equals(nextCursorMark)) {
	            done = true;
	        }
	        cursorMark = nextCursorMark;
	    }
	}
	
	private static HashSet<String> GetNonValidFields(SolrClient sourceClient) throws Exception {
		SolrQuery query = new SolrQuery();
	    query.add(CommonParams.QT, "/schema/copyfields");
	    QueryResponse response;
	    HashSet<String> results = new HashSet<String>();
		try {
			response = SolrErrorHandling.Query(sourceClient, query);
			
		//TODO: cast to map? 	
	    List<SimpleOrderedMap> fields = (List<SimpleOrderedMap>) response.getResponse().get("copyFields");
	    for (SimpleOrderedMap f: fields) {
	    	results.add(f.toString().replace("{", "").replace("}", "").split(",")[1].split("=")[1]);
	    }
//	    query.clear();
//	    query.add(CommonParams.QT, "/schema/dynamicfields");
//	    response = SolrErrorHandling.Query(sourceClient, query);
//	    
//	    fields = (List<SimpleOrderedMap>) response.getResponse().get("dynamicFields");
//	    for (SimpleOrderedMap m: fields) {
//	    	results.add(m.get("name").toString());
//	    }
//	    results.remove("wr_svcs_hasservice"); //TODO: check why
//	    results.remove("wr_dcterms_isReferencedBy"); 
	    return results;
		} catch (SolrServerException | IOException e) {
			logger.fatal("Error reading original schema from sourceClient: "+ e.getMessage());
			throw e;
		}
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
		Integer buffersize = Integer.parseInt(p.getProperty("buffersize"));
		Integer records = Integer.parseInt(p.getProperty("records"));
		HashSet<String> nvfields = GetNonValidFields(sourceClient);
		Index(sourceClient,targetClient,buffersize,nvfields,records);
		} catch (Exception e) {
			logger.fatal("Fatal error" + e.getMessage());
			e.printStackTrace();
			throw e;
		}
	}

}
