package europeana.evaluation.ga;

import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.PrintWriter;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.security.GeneralSecurityException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Properties;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

import org.apache.log4j.Logger;
import org.apache.log4j.PropertyConfigurator;
import org.apache.solr.client.solrj.SolrClient;
import org.apache.solr.client.solrj.SolrQuery;
import org.apache.solr.client.solrj.SolrServerException;
import org.apache.solr.client.solrj.impl.HttpSolrClient;
import org.apache.solr.client.solrj.response.QueryResponse;
import org.apache.solr.common.SolrDocument;

import com.google.api.services.analyticsreporting.v4.model.ColumnHeader;
import com.google.api.services.analyticsreporting.v4.model.DateRange;
import com.google.api.services.analyticsreporting.v4.model.DateRangeValues;
import com.google.api.services.analyticsreporting.v4.model.Dimension;
import com.google.api.services.analyticsreporting.v4.model.GetReportsResponse;
import com.google.api.services.analyticsreporting.v4.model.Metric;
import com.google.api.services.analyticsreporting.v4.model.Report;
import com.google.api.services.analyticsreporting.v4.model.ReportRequest;
import com.google.api.services.analyticsreporting.v4.model.ReportRow;

import europeana.utils.GoogleAnalytics;
import europeana.utils.SolrErrorHandling;
import europeana.utils.Utils;


/***
 * Software to get insights from logs in Google Analytics.
 * For the moment it generates a sample of the queries done and attach information about their existence as labels or part of the contents of the entities in our Entity Collection. 
 * @author mmarrero
 * 
 */

public class Process {
	
	static Logger logger = Logger.getLogger(Process.class);
	

	
	public static void main(String[] args) throws Exception {
		
		System.out.println("Processing...");
		InputStream is = Process.class.getClassLoader().getResourceAsStream("resources/log4j.properties");
		PropertyConfigurator.configure(is);
		//PropertyConfigurator.configure("log4j.properties");
		Properties prop;
		prop = Utils.readProperties(Process.class.getClassLoader().getResourceAsStream("resources/config.properties"));
		String startDate = prop.getProperty("start_date");
		String endDate = prop.getProperty("start_date");
		String solrClient = prop.getProperty("solr_entity");
		Integer sampleSize = Integer.parseInt(prop.getProperty("sample_size"));
		String gaSamplingLevel = prop.getProperty("ga_sampling");
		Path gakey = Paths.get(prop.getProperty("gakey"));
		SolrClient client = new HttpSolrClient.Builder(solrClient).build();

		QueryList<EntityQuery> entityList = new QueryList<EntityQuery>(gakey, startDate, endDate, gaSamplingLevel, client);
		entityList.Filter_SimpleQueries();
		entityList.Filter_UniquePageViews(10);
		//entityList.Sample(sampleSize);
		
		OutputStream os_entity = new FileOutputStream("query_sample_entity.csv"); 
		entityList.Print(os_entity);
		os_entity.close();
		System.out.println("Done. Created file query_sample_entity.csv");
		
		
		QueryList<BasicQuery> basicList = new QueryList<BasicQuery>(gakey, startDate, endDate, gaSamplingLevel, client);
		basicList.Filter_SimpleQueries();
		basicList.Filter_Collection("world-war-I"); //Filter by 1914-18 thematic collection
		Set<String> languages = new HashSet<String>();
		basicList.getQueries().forEach(p -> languages.add(p.getLanguage()));
		Integer sample = sampleSize / languages.size();
		List<BasicQuery> listQueries = new ArrayList<BasicQuery>();
		for (String langTag: languages) {
			QueryList<BasicQuery> langQuery = new QueryList<BasicQuery>(basicList.getQueries());
			langQuery.Filter_Language(langTag);
			if (sample < langQuery.getQueries().size())
				langQuery.Sample(sample);
			listQueries.addAll(langQuery.getQueries());
		}
		QueryList<BasicQuery> langQueries = new QueryList<BasicQuery>(listQueries);
		OutputStream os_lang = new FileOutputStream("query_sample_lang_WWI.csv"); 
		langQueries.Print(os_lang);
		os_lang.close();
		System.out.println("Done. Created file query_sample_lang.csv.  Number of languages: " + languages.size() );


	}
	

}
