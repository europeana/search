package europeana.evaluation.logs;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

import org.apache.log4j.Logger;
import org.json.JSONException;
import org.json.JSONObject;

public class Entry {
	
	static Logger logger = Logger.getLogger(Process.class);
	
	String query;
	String filters;
	Integer hits;
	Map<String, Set<Integer>> clicks = new HashMap<String, Set<Integer>>();
	Set<String> filterType = new HashSet<String>();
	Map<String, Integer> idsClicked = new HashMap<String, Integer>(); //id rank

	public String getQuery() {
		return query;
	}

	public String getFilters() {
		return filters;
	}

	public Integer getHits() {
		return hits;
	}

	public Map<String, Set<Integer>> getClicks() {
		return clicks;
	}
	
	public Map<String, Integer> getIdsClicked() {
		return idsClicked;
	}
	
	public Set<String> getFilterType() {
		return filterType;
	}

	public Entry(String query, String filters, Integer hits) {
		this.query = query;
		this.filters = filters;
		this.hits = hits;
		addFilterTypes(filters);

	}
	
	public void UpdateClicks(String idSession, String idDocument, Integer rank) {
		Set<Integer> ranks;
		if (!this.clicks.containsKey(idSession)) {
			ranks = new HashSet<Integer>();
			this.clicks.put(idSession, ranks);
		}
		ranks = this.clicks.get(idSession);	
		ranks.add(rank);
		idsClicked.put(idDocument, rank); //I am assuming here that for same query/filters, documents are ranked in the same position
	}
	
	private void addFilterTypes(String filters) {
		if (!filters.isEmpty()) {
			try {
				JSONObject json_fil = new JSONObject(filters.replace("\\x00", " ").replace("\\xa0", " "));
				for (String key: json_fil.keySet()) {
					filterType.add(key);
				}
			} catch (JSONException e) {
				logger.warn("Error on entry " + query + " filter: " + filters);
			}
		}
	}
	
	
	

}
