package europeana.evaluation.ga;

import java.io.IOException;
import java.io.OutputStream;
import java.io.PrintWriter;

import org.apache.solr.client.solrj.SolrClient;
import org.apache.solr.client.solrj.SolrServerException;

public class BasicQuery {
	String query;
	String language;
	String collection;
	Integer uniqueSearches;


	
	public String getQuery() {
		return query;
	}
	public String getLanguage() {
		return language;
	}
	public String getPortal() {
		return collection;
	}
	public Integer getUniquePageViews() {
		return uniqueSearches;
	}

	public BasicQuery(String query, String language, String collection, Integer uniqueSearches) {
		this.query = query.replace("\"", "").replaceAll("“",  "").trim();
		this.language = language;
		this.collection = collection;
		this.uniqueSearches = uniqueSearches;
	}
	
	public static BasicQuery CreateQuery(String query, String language, String collection, Integer uniqueSearches) {
		return new BasicQuery(query, language, collection, uniqueSearches);
	}
	
	public static BasicQuery CreateQuery(String query, String language, String collection, Integer uniqueSearches, SolrClient solrClient)  throws SolrServerException, IOException {
		return new BasicQuery(query, language, collection, uniqueSearches);
	}
	

	public void Print(PrintWriter pw) {
		pw.print(this.getQuery());
		pw.print("\t");
		pw.print(this.getPortal());
		pw.print("\t");
		pw.print(this.getLanguage());
		pw.println();
	}
	
}
