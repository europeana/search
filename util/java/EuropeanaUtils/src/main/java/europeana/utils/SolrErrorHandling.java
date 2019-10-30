package europeana.utils;

import java.io.IOException;
import java.io.InputStream;
import java.io.UnsupportedEncodingException;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.Collection;
import java.util.Map;

import org.apache.commons.io.IOUtils;
import org.apache.log4j.Logger;
import org.apache.solr.client.solrj.SolrClient;
import org.apache.solr.client.solrj.SolrQuery;
import org.apache.solr.client.solrj.SolrServerException;
import org.apache.solr.client.solrj.response.QueryResponse;
import org.apache.solr.client.solrj.response.UpdateResponse;
import org.apache.solr.common.SolrInputDocument;
import org.json.JSONObject;

public class SolrErrorHandling {
	static Logger logger = Logger.getLogger(SolrErrorHandling.class);
	
	public static final Integer ATTEMPTS = 3;
	public static final Long SLEEP_MS = 1000l;
	
	public static UpdateResponse commit(SolrClient solr) throws SolrServerException, IOException {
		int attempts = ATTEMPTS;
		while (attempts > 0)
			try {
				UpdateResponse response = solr.commit();
				logger.debug("Commit done ");
				return response;
			} catch (SolrServerException | IOException e) {
				attempts--;
				if (attempts <= 0) {
					throw e;
				}
				try {
					Thread.sleep(SLEEP_MS);
				} catch (InterruptedException e1) {
					logger.warn("Commit Attempt " + (ATTEMPTS - attempts) + " - Thread interrupted");
				}
			}
		return null;
		} 
	
	public static UpdateResponse add(SolrClient solr, Collection<SolrInputDocument> solrDocument) throws SolrServerException, IOException {
		int attempts = ATTEMPTS;
		while (attempts > 0)
			try {
				UpdateResponse response = solr.add(solrDocument);
				logger.debug("Indexing done ");
				return response;
			} catch (SolrServerException | IOException e) {
				attempts--;
				if (attempts <= 0) {
					throw e;
				}
				try {
					Thread.sleep(SLEEP_MS);
				} catch (InterruptedException e1) {
					logger.warn("Indexing Attempt " + (ATTEMPTS - attempts) + " - Thread interrupted");
				}
			}
		return null;
		} 
	
	public static UpdateResponse add(SolrClient solr, String collection, Collection<SolrInputDocument> solrDocument) throws SolrServerException, IOException {
		int attempts = ATTEMPTS;
		while (attempts > 0)
			try {
				UpdateResponse response = solr.add(collection, solrDocument);
				logger.debug("Indexing done ");
				return response;
			} catch (SolrServerException | IOException e) {
				attempts--;
				if (attempts <= 0) {
					throw e;
				}
				try {
					Thread.sleep(SLEEP_MS);
				} catch (InterruptedException e1) {
					logger.warn("Indexing Attempt " + (ATTEMPTS - attempts) + " - Thread interrupted");
				}
			}
		return null;
		} 
	
	public static QueryResponse query(SolrClient solr, String collection, SolrQuery params) throws SolrServerException, IOException {
		int attempts = ATTEMPTS;
		while (attempts > 0)
			try {
				QueryResponse response = solr.query(collection, params);
				logger.debug("Query done ");
				return response;
			} catch (SolrServerException | IOException e) {
				attempts--;
				if (attempts <= 0) {
					throw e;
				}
				try {
					Thread.sleep(SLEEP_MS);
				} catch (InterruptedException e1) {
					logger.warn("Query Attempt " + (ATTEMPTS - attempts) + " - Thread interrupted");				}
			}
		return null;
	} 
	
	public static QueryResponse query(SolrClient solr, SolrQuery params) throws SolrServerException, IOException {
		int attempts = ATTEMPTS;
		while (attempts > 0)
			try {
				QueryResponse response = solr.query(params);
				logger.debug("Query done ");
				return response;
			} catch (SolrServerException | IOException e) {
				attempts--;
				if (attempts <= 0) {
					throw e;
				}
				try {
					Thread.sleep(SLEEP_MS);
				} catch (InterruptedException e1) {
					logger.warn("Query Attempt " + (ATTEMPTS - attempts) + " - Thread interrupted");				}
			}
		return null;
	}
	
	public static JSONObject query(URL solrHttp, Map<String, String> queryParams) throws IOException {
		StringBuffer sb = new StringBuffer();
		for (Map.Entry<String, String> p : queryParams.entrySet()) {
			sb.append(p.getKey() + "=");
			sb.append(URLEncoder.encode(p.getValue(), StandardCharsets.UTF_8.name()));
			sb.append("&");
		}
		sb.append("wt=json");
		URL request = new URL(solrHttp + "?" + sb.toString());
		
		int attempts = ATTEMPTS;
		while (attempts > 0)
			try {
				HttpURLConnection connection = (HttpURLConnection) request.openConnection();
			    connection.setDoOutput(true);
			    connection.setInstanceFollowRedirects(false);
			    connection.setRequestMethod("GET");
			    connection.setRequestProperty("Content-Type", "application/json");
			    connection.setRequestProperty("charset", "utf-8");
			    connection.connect();
			    InputStream is = connection.getInputStream();
			    String jsonStr = IOUtils.toString(is, StandardCharsets.UTF_8);
			    JSONObject json = new JSONObject(jsonStr);
			    return json;
			} catch (IOException e) {
				attempts--;
				if (attempts <= 0) {
					throw e;
				}
				try {
					Thread.sleep(SLEEP_MS);
				} catch (InterruptedException e1) {
					logger.warn("Query Attempt " + (ATTEMPTS - attempts) + " - Thread interrupted");				
				}
			}
	      return null;
	}
	
		
	

}
