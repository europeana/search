package europeana.evaluation.ga;

import java.io.IOException;
import java.io.OutputStream;
import java.io.PrintWriter;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import org.apache.solr.client.solrj.SolrClient;
import org.apache.solr.client.solrj.SolrQuery;
import org.apache.solr.client.solrj.SolrServerException;
import org.apache.solr.client.solrj.response.QueryResponse;
import org.apache.solr.common.SolrDocument;

import europeana.utils.SolrErrorHandling;

public class EntityQuery  extends BasicQuery {
	Set<String> eLabel = new HashSet<String>();; //one of the labels is a match
	Set<String> eText = new HashSet<String>();; //one of the fields in 'text' is a match
	
	Set<String> eRelaxedLabel = new HashSet<String>();; //any parto of the labels is a match
	Set<String> eRelaxedText = new HashSet<String>();; //any part of the field 'text' is a match

	
	public Set<String> geteRelaxedLabel() {
		return eRelaxedLabel;
	}

	public Set<String> geteRelaxedText() {
		return eRelaxedText;
	}

	
	public Set<String> getEntityClassLabel() {
		return eLabel;
	}

	public Set<String> getEntityClassText() {
		return eText;
	}

	public void AddEntityClassLabel(String entityClass) {
		this.eLabel.add(entityClass);
	}
	
	public void AddEntityClassText(String entityClass) {
		this.eText.add(entityClass);
	}
	
	public void AddEntityClassRelaxedLabel(String entityClass) {
		this.eRelaxedLabel.add(entityClass);
	}
	
	public void AddEntityClassRelaxedText(String entityClass) {
		this.eRelaxedText.add(entityClass);
	}

	public EntityQuery(String query, String language, String collection, Integer uniqueSearches, SolrClient solrClient) throws SolrServerException, IOException {
		super(query, language, collection, uniqueSearches);
		AddEntityInfo(solrClient);
	}	
	
	public static EntityQuery CreateQuery(String query, String language, String collection, Integer uniqueSearches, SolrClient solrClient) throws SolrServerException, IOException {
		return new EntityQuery(query, language, collection, uniqueSearches, solrClient);
	}
	
	public void AddEntityInfo (SolrClient solrClient) throws SolrServerException, IOException {
		String queryLC = this.getQuery().toLowerCase();
		SolrQuery query = new SolrQuery();
		String solr_query = "skos_prefLabel:\"" + queryLC + "\" OR label:\"" + queryLC + "\" OR text:\"" + queryLC + "\"";
		query.setQuery(solr_query);
		QueryResponse response = SolrErrorHandling.Query(solrClient, query);
		for (SolrDocument doc: response.getResults()) {
			Set<String> labels = new HashSet<String>();
			Set<String> text = new HashSet<String>();
			String type = doc.getFieldValue("type").toString();
			labels.add(doc.getFieldValue("skos_prefLabel").toString().toLowerCase());
			doc.getFieldValues("label").forEach(p -> labels.add(p.toString().toLowerCase()));
			doc.getFieldValues("text").forEach(p -> text.add(p.toString().toLowerCase()));
			if (labels.contains(queryLC)) {
				this.AddEntityClassLabel(type);
			}
			if (text.contains(queryLC)) {
				this.AddEntityClassText(type);
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
				this.AddEntityClassRelaxedLabel(type);
			}
			wholeEntity = true;
			for (String item : keywords) {
				if (!textParts.contains(item)) {
					wholeEntity = false;
					break;
				}
			}
			if (wholeEntity) {
				this.AddEntityClassRelaxedText(type);
			}
		}
	}

	
	@Override public void Print(PrintWriter pw){
		pw.print(this.getQuery());
		pw.print("\t");
		pw.print(this.getPortal());
		pw.print("\t");
		pw.print(this.getLanguage());
		pw.print("\t");
		pw.print(this.getEntityClassLabel());
		pw.print("\t");
		pw.print(this.getEntityClassText());
		pw.print("\t");
		pw.print(this.geteRelaxedLabel());
		pw.print("\t");
		pw.print(this.geteRelaxedText());
		pw.println();
	}
	
	
}


