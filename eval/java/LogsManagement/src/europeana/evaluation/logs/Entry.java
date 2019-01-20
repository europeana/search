package europeana.evaluation.logs;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

public class Entry {
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

	String query;
	String filters;
	Integer hits;
	Map<String, Set<Integer>> clicks = new HashMap<String, Set<Integer>>();

	Map<String, Integer> idsClicked = new HashMap<String, Integer>(); //id rank


	
	public Entry(String query, String filters, Integer hits) {
		this.query = query;
		this.filters = filters;
		this.hits = hits;
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
	

}
