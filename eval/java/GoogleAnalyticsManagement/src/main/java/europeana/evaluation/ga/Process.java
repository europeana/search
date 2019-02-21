package europeana.evaluation.ga;


import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.PrintWriter;
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

public class Process {
	
	//private static final String URL_PATTERN = "/portal/(?<lang>.*?)/(search|collections/(?<cname>.+?))\\?.*?q\\=(?<query>.*?)(&|$)";
	private static final String URL_PATTERN = "/portal/(?<lang>[^/]+)(/collections/(?<cname>.+?)\\?)?";
	private static final Pattern pattern = Pattern.compile(URL_PATTERN);

	
	private static List<Query> GetQueries(GetReportsResponse response) throws Exception {
		List<Query> queries = new ArrayList<Query>();
		
		for (Report report: response.getReports()) {
			ColumnHeader header = report.getColumnHeader();
			List<String> dimensionHeaders = header.getDimensions();
			int indexPage = dimensionHeaders.indexOf("ga:searchStartPage");
			int indexTerm = dimensionHeaders.indexOf("ga:searchKeyword");
			//List<MetricHeaderEntry> metricHeaders = header.getMetricHeader().getMetricHeaderEntries();
			List<ReportRow> rows = report.getData().getRows();
			
			for (ReportRow row: rows) {
				List<String> dimensions = row.getDimensions();
				List<DateRangeValues> metrics = row.getMetrics();
				String dim = dimensions.get(indexPage);
				String query = dimensions.get(indexTerm);
				Matcher matcher = pattern.matcher(dim);
				if (matcher.find()) {
					String lang = matcher.group("lang");
					String cname = matcher.group("cname");
					if (cname == null) {
						cname = "portal";
					}
					//String query = matcher.group("query");
					Integer uniqueViews = Integer.parseInt(metrics.get(0).getValues().get(0));
					queries.add(new Query(query, lang, cname, uniqueViews));
				} else {
					System.out.println("Not processed ga:searchStartPage = " + dim);
					//throw new IllegalArgumentException("Regex didn't recognize dimension " + report.getColumnHeader().getDimensions().get(indexPage) + ": " + dim);
				}
			}
		}
		return queries;
	}
	
	private static List<Query> Sample(List<Query> queries, Integer sampleSize){
		Collections.shuffle(queries);
		return queries.subList(0, sampleSize);
	}

	private static List<Query> Filter(List<Query> queries){
		return queries.stream().filter(p -> (!p.query.contains("*") && !p.query.contains(":") && p.uniqueSearches <= 10 && p.query.matches("[\"\'\\“A-Za-z\\s]+") && !p.query.contains("AND") && !p.query.contains("OR") && !p.query.startsWith("<") && p.query.length() > 2)).collect(Collectors.toList());
	}
	
	private static void AddEntityInfo(List<Query> queries, String solrClient) throws SolrServerException, IOException {
		SolrClient client = new HttpSolrClient.Builder(solrClient).build();
		for (Query q: queries) {
			String queryLC = q.getQuery().toLowerCase();
			SolrQuery query = new SolrQuery();
			String solr_query = "skos_prefLabel:\"" + queryLC + "\" OR label:\"" + queryLC + "\" OR text:\"" + queryLC + "\"";
			System.out.println(solr_query);
			query.setQuery(solr_query);
			QueryResponse response = SolrErrorHandling.Query(client, query);
			for (SolrDocument doc: response.getResults()) {
				Set<String> labels = new HashSet<String>();
				Set<String> text = new HashSet<String>();
				String type = doc.getFieldValue("type").toString();
				labels.add(doc.getFieldValue("skos_prefLabel").toString().toLowerCase());
				doc.getFieldValues("label").forEach(p -> labels.add(p.toString().toLowerCase()));
				doc.getFieldValues("text").forEach(p -> text.add(p.toString().toLowerCase()));
				if (labels.contains(queryLC)) {
					q.AddEntityClassLabel(type);
				}
				if (text.contains(queryLC)) {
					q.AddEntityClassText(type);
				}
				
				String[] keywords = queryLC.split(" ");
				Set<String> labelParts = new HashSet<String>(Arrays.asList(labels.toString().split("[\\W_]")));
				Set<String> textParts = new HashSet<String>(Arrays.asList(text.toString().split("[\\W_]")));
				boolean wholeEntity = true;
				for (String item : keywords) {
					if (!labelParts.contains(item)) {
						wholeEntity = false;
						break;
					}
				}
				if (wholeEntity) {
					q.AddEntityClassRelaxedLabel(type);
				}
				wholeEntity = true;
				for (String item : keywords) {
					if (!textParts.contains(item)) {
						wholeEntity = false;
						break;
					}
				}
				if (wholeEntity) {
					q.AddEntityClassRelaxedText(type);
				}
			}
		}
	}
	
	private static GetReportsResponse GoogleAnalyticsRequest(String startDate, String endDate, String gaSamplingLevel) throws GeneralSecurityException, IOException {
		// Create the DateRange object.
		DateRange dateRange = new DateRange();
		dateRange.setStartDate(startDate);
		dateRange.setEndDate(endDate);

		// Create the Metrics object.
		Metric searches = new Metric().setExpression("ga:searchUniques");

		// Create the dimension object.
		Dimension sterms = new Dimension().setName("ga:searchKeyword");
		Dimension startPage = new Dimension().setName("ga:searchStartPage");

		// Create the ReportRequest object.
		ReportRequest request = new ReportRequest()
				.setDateRanges(Arrays.asList(dateRange))
				.setMetrics(Arrays.asList(searches))
				.setFiltersExpression("ga:searchStartPage!@(entrance);ga:searchStartPage!@(other)")
				//.setOrderBys(Arrays.asList(order))
				.setSamplingLevel(gaSamplingLevel)
				.setDimensions(Arrays.asList(sterms, startPage));
				//.setPageSize(10000);
	
		europeana.utils.GoogleAnalytics ga = new GoogleAnalytics();
		return ga.GetRequest(request);
	}
	
	private static void Print(OutputStream os, List<Query> queries) {
		PrintWriter pw = new PrintWriter(os);
		queries.forEach(p -> {
			pw.print(p.query);
			pw.print("\t");
			pw.print(p.collection);
			pw.print("\t");
			pw.print(p.language);
			pw.print("\t");
			pw.print(p.eLabel.toString());
			pw.print("\t");
			pw.print(p.eText.toString());
			pw.print("\t");
			pw.print(p.eRelaxedLabel.toString());
			pw.print("\t");
			pw.print(p.eRelaxedText.toString());
			pw.println();
		});
		pw.close();
	}
	
	public static void main(String[] args) throws Exception {
		
		System.out.println("Processing...");
		InputStream is = Process.class.getClassLoader().getResourceAsStream("log4j.properties");
		PropertyConfigurator.configure(is);
		Properties prop;
		prop = Utils.readProperties(Process.class.getClassLoader().getResourceAsStream("config.properties"));
		String startDate = prop.getProperty("start_date");
		String endDate = prop.getProperty("start_date");
		String solrClient = prop.getProperty("solr_entity");
		Integer sampleSize = Integer.parseInt(prop.getProperty("sample_size"));
		String gaSamplingLevel = prop.getProperty("ga_sampling");


		GetReportsResponse gaResponse = GoogleAnalyticsRequest(startDate, endDate, gaSamplingLevel);
		List<Query> queries = GetQueries(gaResponse);
		queries = Filter(queries);
		queries = Sample(queries, sampleSize);
		
		AddEntityInfo(queries, solrClient);
		OutputStream file = new FileOutputStream("query_sample.csv"); 
		Print(file, queries);
		file.close();
	}
	

}
