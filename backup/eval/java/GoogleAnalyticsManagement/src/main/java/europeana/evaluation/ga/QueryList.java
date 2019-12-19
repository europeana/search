package europeana.evaluation.ga;

import java.io.IOException;
import java.io.OutputStream;
import java.io.PrintWriter;
import java.nio.file.Path;
import java.security.GeneralSecurityException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.Collections;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

import org.apache.log4j.Logger;
import org.apache.solr.client.solrj.SolrClient;

import com.google.api.services.analyticsreporting.v4.model.ColumnHeader;
import com.google.api.services.analyticsreporting.v4.model.DateRange;
import com.google.api.services.analyticsreporting.v4.model.DateRangeValues;
import com.google.api.services.analyticsreporting.v4.model.Dimension;
import com.google.api.services.analyticsreporting.v4.model.GetReportsRequest;
import com.google.api.services.analyticsreporting.v4.model.GetReportsResponse;
import com.google.api.services.analyticsreporting.v4.model.Metric;
import com.google.api.services.analyticsreporting.v4.model.Report;
import com.google.api.services.analyticsreporting.v4.model.ReportRequest;
import com.google.api.services.analyticsreporting.v4.model.ReportRow;

import europeana.utils.GoogleAnalytics;

public class QueryList<T extends BasicQuery> {
	
	static Logger logger = Logger.getLogger(QueryList.class);
	
	//private static final String URL_PATTERN = "/portal/(?<lang>[^/]+)(/collections/(?<cname>.+?)\\?)?";
	//private static final Pattern pattern = Pattern.compile(URL_PATTERN);
	private static final String COLLECTIONS = "/collections/(?<cname>[^/\\?]+)";
	private static final String PORTAL = "/portal/(?<lang>[^/\\?]+)";
	private static final String QUERY = "q=(?<query>[^/\\?\\&]+)";
	private static final Pattern collectionsPat = Pattern.compile(COLLECTIONS);
	private static final Pattern portalPat = Pattern.compile(PORTAL);
	private static final Pattern queryPat = Pattern.compile(QUERY);
	
	private List<T>queries;
	
	public List<T> getQueries() {
		return queries;
	}

	public void setQueries(List<T> queries) {
		this.queries = queries;
	}

	
	public QueryList(Path gakey, String startDate, String endDate, String gaSamplingLevel, SolrClient solrClient) throws Exception {
		GetReportsResponse gaResponse = GoogleAnalyticsRequest(gakey, startDate, endDate, gaSamplingLevel);
		setQueries(GetQueries(gaResponse, solrClient));
	}
	
	public QueryList(List<T> qlist) {
		setQueries(qlist);
	}
	
//	private static GetReportsResponse GoogleAnalyticsRequest(Path gakey, String startDate, String endDate, String gaSamplingLevel) throws GeneralSecurityException, IOException {
//		// Create the DateRange object.
//		DateRange dateRange = new DateRange();
//		dateRange.setStartDate(startDate);
//		dateRange.setEndDate(endDate);
//
//		// Create the Metrics object.
//		Metric views = new Metric().setExpression("ga:pageviews");
//
//		// Create the dimension object.
//		//Dimension sterms = new Dimension().setName("ga:searchKeyword");
//		Dimension startPage = new Dimension().setName("ga:pagePath");
//
//		// Create the ReportRequest object.
//		ReportRequest request = new ReportRequest()
//				.setDateRanges(Arrays.asList(dateRange))
//				.setMetrics(Arrays.asList(views))
//				//.setFiltersExpression("ga:searchStartPage!@(entrance);ga:searchStartPage!@(other)")
//				//.setOrderBys(Arrays.asList(order))
//				.setSamplingLevel(gaSamplingLevel)
//				.setPageSize(100000)
//				.setDimensions(Arrays.asList(startPage));
//				//.setPageSize(10000);
//	
//		europeana.utils.GoogleAnalytics ga = new GoogleAnalytics(gakey);
//		return ga.GetRequest(request);
//	}
//
//	@SuppressWarnings("unchecked")
//	private List<T> GetQueries(GetReportsResponse response, SolrClient solrClient) throws Exception {
//		List<T> queries = new ArrayList<T>();
//		
//		for (Report report: response.getReports()) {
//			ColumnHeader header = report.getColumnHeader();
//			List<String> dimensionHeaders = header.getDimensions();
//			int indexPage = dimensionHeaders.indexOf("ga:pagePath");
//			//int indexTerm = dimensionHeaders.indexOf("ga:searchKeyword");
//			//List<MetricHeaderEntry> metricHeaders = header.getMetricHeader().getMetricHeaderEntries();
//			List<ReportRow> rows = report.getData().getRows();
//			
//			for (ReportRow row: rows) {
//				List<String> dimensions = row.getDimensions();
//				List<DateRangeValues> metrics = row.getMetrics();
//				String dim = dimensions.get(indexPage);
//				if (dim.contains("world-war"))
//					System.out.println(dim);
//				
//				Matcher matcherPortal = portalPat.matcher(dim);
//				Matcher matcherCollections = collectionsPat.matcher(dim);
//				Matcher matcherQuery = queryPat.matcher(dim);
//				String lang,cname,query;
//				
//				if (matcherPortal.find() && matcherQuery.find()) {
//					lang = matcherPortal.group("lang");
//					if (matcherCollections.find()) {
//						cname = matcherCollections.group("cname");
//					} else {
//						cname = "portal";
//					}
//					query = matcherQuery.group("query");
//					
//					//String query = matcher.group("query");
//					Integer uniqueViews = Integer.parseInt(metrics.get(0).getValues().get(0));
//					
//					
//					queries.add((T) T.CreateQuery(query, lang, cname, uniqueViews, solrClient));
//				} else {
//					System.out.println("Not processed ga:searchStartPage = " + dim);
//					//throw new IllegalArgumentException("Regex didn't recognize dimension " + report.getColumnHeader().getDimensions().get(indexPage) + ": " + dim);
//				}
//			}
//		}
//		return queries;
//	}
	
	private static GetReportsResponse GoogleAnalyticsRequest(Path gakey, String startDate, String endDate, String gaSamplingLevel) throws GeneralSecurityException, IOException {
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
				.setPageSize(100000)
				.setDimensions(Arrays.asList(sterms, startPage));
				//.setPageSize(10000);

//		GetReportsRequest reportRequest = new GetReportsRequest();
//		reportRequest.setReportRequests(Arrays.asList(request));
//		reportRequest.setUseResourceQuotas(true);
		
		europeana.utils.GoogleAnalytics ga = new GoogleAnalytics(gakey);
		return ga.GetRequest(request);
	}

	@SuppressWarnings("unchecked")
	private List<T> GetQueries(GetReportsResponse response, SolrClient solrClient) throws Exception {
		List<T> queries = new ArrayList<T>();
		
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
				Matcher matcherPortal = portalPat.matcher(dim);
				Matcher matcherCollections = collectionsPat.matcher(dim);
				String lang,cname;
				
				if (matcherPortal.find()) {
					lang = matcherPortal.group("lang");
					if (matcherCollections.find()) {
						cname = matcherCollections.group("cname");
					} else {
						cname = "portal";
					}

					
					//String query = matcher.group("query");
					Integer uniqueViews = Integer.parseInt(metrics.get(0).getValues().get(0));
					
					
					queries.add((T) T.CreateQuery(query, lang, cname, uniqueViews, solrClient));
				} else {
					System.out.println("Not processed ga:searchStartPage = " + dim);
					//throw new IllegalArgumentException("Regex didn't recognize dimension " + report.getColumnHeader().getDimensions().get(indexPage) + ": " + dim);
				}
			}
		}
		return queries;
	}
	
	public void Sample(Integer sampleSize){
		Collections.shuffle(this.getQueries());
		this.setQueries(queries.subList(0, sampleSize));
	}
	
	
	public void Filter_SimpleQueries(){
		this.setQueries(queries.stream().filter(p -> (p.getQuery().matches("[\"\'\\“A-Za-z\\s]+") && !p.getQuery().contains("AND") && !p.query.contains("OR") && !p.query.contains(":") && p.getQuery().length() > 2)).collect(Collectors.toList()));
	}
	
	//TODO: check unique page views <= 10
	public void Filter_UniquePageViews(Integer lessEqualThan) {
		this.setQueries(queries.stream().filter(p -> (p.getUniquePageViews() <= 10)).collect(Collectors.toList()));
	}
	
	public void Filter_Language(String langTag) {
		this.setQueries(queries.stream().filter(p -> (p.getLanguage().equalsIgnoreCase(langTag))).collect(Collectors.toList()));
	}
	
	public void Filter_Collection(String collection) {
		this.setQueries(queries.stream().filter(p -> (p.getPortal().equalsIgnoreCase(collection))).collect(Collectors.toList()));
	}
	
	public void Print(OutputStream os) {
		PrintWriter pw = new PrintWriter(os);
		this.getQueries().forEach(p -> p.Print(pw));
		pw.close();

	}


}
