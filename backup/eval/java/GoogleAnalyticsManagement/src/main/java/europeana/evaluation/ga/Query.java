package europeana.evaluation.ga;


import java.util.HashSet;
import java.util.Set;

public class Query {
	String query;
	String language;
	String collection;
	Integer uniqueSearches;
	Set<String> eLabel; //one of the labels is a match
	Set<String> eText; //one of the fields in 'text' is a match
	
	Set<String> eRelaxedLabel; //any parto of the labels is a match
	Set<String> eRelaxedText; //any part of the field 'text' is a match

	
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

	public Set<String> getEntityClassLabel() {
		return eLabel;
	}

	public Set<String> getEntityClassText() {
		return eText;
	}
	
	public Query(String query, String language, String collection, Integer uniqueSearches) {
		this.query = query.replace("\"", "").replaceAll("“",  "").trim();
		this.language = language;
		this.collection = collection;
		this.uniqueSearches = uniqueSearches;
		this.eLabel = new HashSet<String>();
		this.eText = new HashSet<String>();
		this.eRelaxedLabel = new HashSet<String>();
		this.eRelaxedText = new HashSet<String>();
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


}
