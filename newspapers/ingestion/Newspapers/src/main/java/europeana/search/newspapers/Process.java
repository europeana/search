/*
 * Software to ingest the newspaper collection from the zip files containing the XML information related to full-text
 * It involves a merge between that information and the  metadata contained currently in the metadata index
 * A validation process can be run (in config.properties) in order to check that the record generated contains exactly the same metadata
 * author:mmarrero
 */

package europeana.search.newspapers;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.net.URL;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Collection;
import java.util.Enumeration;
import java.util.HashSet;
import java.util.List;
import java.util.Properties;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.zip.ZipEntry;
import java.util.zip.ZipException;
import java.util.zip.ZipFile;

import org.apache.log4j.Logger;
import org.apache.log4j.PropertyConfigurator;
import org.apache.solr.client.solrj.SolrClient;
import org.apache.solr.client.solrj.SolrQuery;
import org.apache.solr.client.solrj.SolrServerException;
import org.apache.solr.client.solrj.impl.CloudSolrClient;
import org.apache.solr.client.solrj.impl.ConcurrentUpdateSolrClient;
import org.apache.solr.client.solrj.impl.HttpSolrClient;
import org.apache.solr.client.solrj.response.QueryResponse;
import org.apache.solr.common.SolrDocument;
import org.apache.solr.common.SolrInputDocument;
import org.apache.solr.common.params.CommonParams;
import org.apache.solr.common.util.SimpleOrderedMap;

import europeana.utils.Buffer;
import europeana.utils.ExceptionThreadFactory;
import europeana.utils.SolrErrorHandling;
import europeana.utils.Utils;


public class Process {
	static Logger logger = Logger.getLogger(Process.class);
	static Buffer<SolrInputDocument> buffer; 
	

	
//TODO: remove collection name, error handling
	private static HashSet<String> GetNonValidFields(SolrClient queryClient, String queryCollection) throws Exception {
		SolrQuery query = new SolrQuery();
	    query.add(CommonParams.QT, "/schema/copyfields");
	    QueryResponse response;
	    HashSet<String> results = new HashSet<String>();
		try {
			response = SolrErrorHandling.Query(queryClient, queryCollection, query);
			
		//TODO: cast to map? 	
	    List<SimpleOrderedMap> fields = (List<SimpleOrderedMap>) response.getResponse().get("copyFields");
	    for (SimpleOrderedMap f: fields) {
	    	results.add(f.toString().replace("{", "").replace("}", "").split(",")[1].split("=")[1]);
	    }
	    query.clear();
	    query.add(CommonParams.QT, "/schema/dynamicfields");
	    response = SolrErrorHandling.Query(queryClient, queryCollection, query);
	    
	    fields = (List<SimpleOrderedMap>) response.getResponse().get("dynamicFields");
	    for (SimpleOrderedMap m: fields) {
	    	results.add(m.get("name").toString());
	    }
	    results.remove("wr_svcs_hasservice");
	    results.remove("wr_dcterms_isReferencedBy"); 
	    return results;
		} catch (SolrServerException | IOException e) {
			logger.fatal("Error reading original schema from queryClient: "+ e.getMessage());
			throw e;
		}
	}
	
	private static HashSet<String> GetSupportedLanguages(SolrClient queryClient) throws Exception {
		SolrQuery query = new SolrQuery();
	    query.add(CommonParams.QT, "/schema/fields");
	    QueryResponse response;
	    HashSet<String> results = new HashSet<String>();
		try {
			response = SolrErrorHandling.Query(queryClient, query);
			List<SimpleOrderedMap> fields = (List<SimpleOrderedMap>) response.getResponse().get("fields");
			for (SimpleOrderedMap m: fields) {
				String fname = m.get("name").toString();
				if (fname.startsWith("fulltext.")) {
					String lang = fname.replace("fulltext.", "");
					if (!lang.isEmpty()) {
						results.add(lang);
					}
				}
			}
	    return results;
		} catch (SolrServerException | IOException e) {
			logger.fatal("Error reading original schema from queryClient: "+ e.getMessage());
			throw e;
		}
	}
	

	private static void IndexFolder(SolrClient indexClient, SolrClient queryClient, String queryCollection, Path datafolder, Integer threadNumber, HashSet<String> nvfields, Integer buffersize, HashSet<String> supplangs) {
		try { 
			File[] files = datafolder.toFile().listFiles();
			ExceptionThreadFactory threadFactory = new ExceptionThreadFactory();
			ExecutorService pool = Executors.newFixedThreadPool(threadNumber, threadFactory);
			buffer = new Buffer<SolrInputDocument>(buffersize);
			for (File file : files) {
				if (file.isFile()) {
					try {
						ZipFile zipFile = new ZipFile(file);
						Enumeration<? extends ZipEntry> entries = zipFile.entries();
						logger.info("Processing dataset "+file.getName());
						int entriesCount = 0;
						while(entries.hasMoreElements()){
							entriesCount++;
							ZipEntry entry = entries.nextElement();
							threadFactory.setName(file.getName() + "." + entry.getName());
							pool.execute(new IndexFile(zipFile, entry, buffer, indexClient, queryClient, queryCollection, nvfields, supplangs));
						}
						logger.info("Processed dataset "+file.getName() + " with " + entriesCount + " entries ");
						//zipFile.close();
					} catch (ZipException e) {
						logger.error("Zip file error: "+file.getName());
						e.printStackTrace();
					} catch (IOException e) {
						logger.error("IO error: "+file.getName());
						e.printStackTrace();
					}
				}
			}
			pool.shutdown();
			pool.awaitTermination(Integer.MAX_VALUE, TimeUnit.DAYS);
			if (!buffer.isEmpty()) {
				indexClient.add(buffer.Retrieve());
				//SolrErrorHandling.Commit(indexClient); //This is already done automatically according to the Solr configuration in solrconfig.xml
				logger.info("Indexed documents batch "+ buffer.GetItemsBuffered() / buffer.GetCapacity() + " - Total documents indexed: " + buffer.GetItemsBuffered());
				
			}
			
			//TEST
			System.out.println("Checking. Different items indexed: "+buffer.GetItemsBuffered());
			System.out.println("Checking. Different ids indexed: "+buffer.ids.size());
			System.out.println("Done. Note that the results may be take some time to be updated in Solr depending on the configuration");
		} catch (InterruptedException e) {
			logger.fatal("Thread pool error: "+ e.getMessage());
			e.printStackTrace();
		} catch (SolrServerException e) {
			logger.fatal("Solr Error during last commit: " + e.getMessage());
			e.printStackTrace();
		} catch (IOException e) {
			logger.fatal("IO/Error during last commit: " + e.getMessage());
			e.printStackTrace();
		}
		
	}
	
	private static void Validate(SolrClient indexClient, SolrClient queryClient, String queryCollection, Integer nrecords) throws SolrServerException, IOException, InterruptedException {
		logger.info("Starting validation on " +  nrecords +" records");
		SolrQuery query = new SolrQuery();
		query.setQuery("*:*");
		query.setParam("rows", nrecords.toString());
		QueryResponse response = null;
		response = SolrErrorHandling.Query(indexClient, query);
		int count = 0;
		for (SolrDocument indexDoc: response.getResults()) {
			Boolean chck = true;
			String europeana_id = indexDoc.getFieldValue("europeana_id").toString();
			query.setQuery("europeana_id"+":"+"\""+ europeana_id + "\"");
			QueryResponse metisResponse = SolrErrorHandling.Query(queryClient, queryCollection, query);
			SolrDocument metadataDoc = metisResponse.getResults().get(0);
			chck = chck && indexDoc.getFieldNames().containsAll(metadataDoc.getFieldNames());
		
			for (String f: metadataDoc.getFieldNames()) {
				if (!f.equalsIgnoreCase("_version_") && !f.equalsIgnoreCase("timestamp") && !f.equalsIgnoreCase("is_fulltext")) {
					Collection<Object> indexvalues = indexDoc.getFieldValues(f);
					Collection<Object> testvalues = metadataDoc.getFieldValues(f);
					chck = chck && indexvalues.containsAll(testvalues);
					chck = chck && testvalues.containsAll(indexvalues);
				}
			}
			if (!chck) {
				logger.error("Record " +  europeana_id + " does not correspond to original metadata");
			}
			count++;
		}
		logger.info("Validation completed: "+ count + " records checked");
	}
	
	
	public static void main(String[] args) throws Exception {
		URL indexClientURL = null;
		URL queryClientURL = null;
		Path datafolder = null;
		Integer threadNumber = null;
		String indexClientType = null;
		Integer buffersize = null;
		String process;
		Integer nrecords = null;
		String queryCollection = null;
		try {
			InputStream is = Process.class.getClassLoader().getResourceAsStream("resources/log4j.properties");
			PropertyConfigurator.configure(is);
					
			Properties p = Utils.readProperties(Process.class.getClassLoader().getResourceAsStream("resources/config.properties"));
			indexClientURL =  new URL(p.getProperty("solrindex"));
			queryClientURL = new URL(p.getProperty("solrquery"));
			queryCollection = p.getProperty("solrquery_collection");
			datafolder = Paths.get(p.getProperty("datafolder"));
			threadNumber = Integer.valueOf(p.getProperty("threads"));
			indexClientType = p.getProperty("solrindextype");
			buffersize = Integer.valueOf(p.getProperty("buffersize"));
			process = p.getProperty("process");
			nrecords = Integer.valueOf(p.getProperty("nrecords"));
			SolrClient queryClient = new CloudSolrClient.Builder().withSolrUrl(queryClientURL.toString()).build();
			SolrClient indexClient = null;
			switch (indexClientType) {
				case "single": indexClient = new HttpSolrClient.Builder(indexClientURL.toString()).build();break;
				case "concurrent": indexClient = new ConcurrentUpdateSolrClient.Builder(indexClientURL.toString()).build();break;
				case "cloud": new CloudSolrClient.Builder().withSolrUrl(indexClientURL.toString()).build();break;
				default: throw new IllegalArgumentException(indexClientType + " not recognized as a type of Solr Client");
			}
			
			if (process.equals("index")) {
				HashSet<String> nvfields = GetNonValidFields(queryClient, queryCollection);
				HashSet<String> ftfields = GetSupportedLanguages(indexClient);
				IndexFolder(indexClient, queryClient, queryCollection, datafolder, threadNumber, nvfields, buffersize, ftfields);
			} else if (process.equals("validate")){
					Validate(indexClient, queryClient, queryCollection, nrecords);
			}
		} catch (Exception e) {
			logger.fatal("Fatal error" + e.getMessage());
			e.printStackTrace();
			throw e;
		} 

	}

}
