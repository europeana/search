package europeana.evaluation.logs;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class Session {

	List<String> queries = new ArrayList<String>();
	List<String> filters = new ArrayList<String>();
	Set<String> filterType = new HashSet<String>();
	Integer clicks = 0;
	String idSession;

	public String getIdSession() {
		return idSession;
	}
	public List<String> getQueries() {
		return queries;
	}
	public List<String> getFilters() {
		return filters;
	}
	public Integer getClicks() {
		return clicks;
	}
	
	public Set<String> getFilterType() {
		return filterType;
	}
	
	public Session(String idSession) {
		this.idSession = idSession;
	}
	
	public void addQuery(String query) {
		queries.add(query);
	}
	
	public void addFilter(String filter) {
		filters.add(filter);
	}
	
	public void addFilterType(String fType) {
		filterType.add(fType);
	}
	
	public void addClick() {
		clicks++;
	}

}
