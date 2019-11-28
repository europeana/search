package europeana.evaluation.logs;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import org.apache.log4j.Logger;
import org.json.JSONException;
import org.json.JSONObject;

public class Session {
	
	static Logger logger = Logger.getLogger(Process.class);

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
		addFilterTypes(filter);
	}
	
	public void addClick() {
		clicks++;
	}
	
	private void addFilterTypes(String filters) {
		if (!filters.isEmpty()) {
			try {
				JSONObject json_fil = new JSONObject(filters.replace("\\x00", " ").replace("\\xa0", " "));
				for (String key: json_fil.keySet()) {
					filterType.add(key);
				}
			} catch (JSONException e) {
				logger.warn("Error on session " + this.getIdSession() + " filter: " + filters);
			}
		}
	}

}
