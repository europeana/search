package europeana.evaluation.logs;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.PrintWriter;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.OptionalInt;
import java.util.Properties;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.IntStream;
import java.util.stream.Stream;

import org.apache.log4j.Logger;
import org.apache.log4j.PropertyConfigurator;
import org.json.JSONException;
import org.json.JSONObject;

import europeana.utils.Utils;

/***
 * Software to get insights from logs coming from ELK.
 * Generates TREC_EVAL files to calculate performance measures from logs (assuming a document clicked is relevant)
 * The logs are assumed to be contained in a folder resulting from applying Tim's code log_extractor.session_extractor and log_extractor.entry_extractor (resulting folder called 'entries_by_session')
 * Important: the filters reflected here do not include those coming from the page in the portal from where that query was launched (eg. search from collection pages)
 * @author mmarrero
 * 
 */

class IntComparator implements Comparator<Integer> {

    @Override
    public int compare(Integer v1, Integer v2) {
        return v1 < v2 ? -1 : v1 > v2 ? +1 : 0;
    }
}

public class Process {
	static Logger logger = Logger.getLogger(Process.class);
	
	private static List<Session> ImportSessions(Path data) throws IOException {
		List<Session> entries = new ArrayList<Session>();
		File[] files = data.toFile().listFiles();
		for (File file: files) {
			if (file.isFile()) {
				String idSession = file.getName().replaceAll(".txt", "");
				Session current = new Session(idSession);
				entries.add(current);
				List<String> lines = Files.readAllLines(file.toPath());
				for (String line: lines) {
					String[] items = line.split("\t");
					if (items.length > 0 && items[0].equals("SearchInteraction") && items.length == 6) {
						String query;
						String filters;
						query = items[3].trim();
						filters = items[4].trim();
						current.addQuery(query);
						current.addFilter(filters);
					} else if (items.length > 0 && items[0].equals("RankedRetrieveRecordInteraction") && items.length == 8) {
						current.addClick();
					}
				}
			}
		}
		return entries;
	}


	
	
	private static List<Entry> ImportEntries(Path data) throws IOException {
		List<Entry> entries = new ArrayList<Entry>();
		File[] files = data.toFile().listFiles();
		for (File file: files) {
			if (file.isFile()) {
				List<String> lines = Files.readAllLines(file.toPath());
				for (String line: lines) {
					String[] items = line.split("\t");
					if (items.length > 0 && items[0].equals("SearchInteraction") && items.length == 6) {
						String query;
						String filters;
						Integer hits;
						query = items[3].trim();
						filters = items[4].trim();
						hits= Integer.parseInt(items[5]);
						Stream<Entry> sameQueries = entries.stream().filter(p -> (p.query.equals(query) && p.filters.equals(filters) && p.hits.equals(hits)));
						if (!sameQueries.findFirst().isPresent()) {
							entries.add(new Entry(query, filters, hits));
						}
					} else if (items.length > 0 && items[0].equals("RankedRetrieveRecordInteraction") && items.length == 8) {
						String query = items[3].trim();
						String filters = items[4].trim();
						Integer hits = Integer.parseInt(items[7]);
						String idSession = items[2];
						String idDocument = items[5];
						Integer rank = Integer.parseInt(items[6]);
						Optional<Entry> sameQueries = entries.stream().filter(p -> (p.query.equals(query) && p.filters.equals(filters) && p.hits.equals(hits))).findFirst();
						Entry current;
						if (!sameQueries.isPresent()) {
							current = new Entry(query, filters, hits);
							entries.add(current);
						} else {
							current = sameQueries.get();
						}
						current.UpdateClicks(idSession, idDocument, rank);
					}
				}
			}
		}
		return entries;
	}
	
	public static void PrintStatisticsSessions(List<Session> entries) {
		System.out.println("Number of sessions: " + entries.size());
		System.out.println("Number of sessions with filter: " + entries.stream().filter(p -> (p.filters.stream().filter(f -> !f.isEmpty()).count() > 0)).count());
		System.out.println("Number of sessions with filter + clicks: " + entries.stream().filter(p -> (p.filters.stream().filter(f -> !f.isEmpty() && (p.clicks > 0)).count() > 0)).count());
		System.out.println("Number of sessions with query keywords: " + entries.stream().filter(p -> (p.queries.stream().filter(q -> (!q.equals("") && !q.equals("NO VALUE PROVIDED") && !q.equals("*") && !q.equals("*:*"))).count()) > 0).count());
		System.out.println("Number of sessions with query keywords + filter: " + entries.stream().filter(p -> ((p.filters.stream().filter(f -> !f.isEmpty()).count() > 0) && (p.queries.stream().filter(q -> (!q.equals("") && !q.equals("NO VALUE PROVIDED") && !q.equals("*") && !q.equals("*:*"))).count()) > 0)).count());
		System.out.println("Number of sessions with clicks: " + entries.stream().filter(p -> (p.clicks > 0)).count());
		System.out.println("Type of filters used and number of sessions where it has been used:");
		Map<String, Integer> filterType = new HashMap<String, Integer>();
		entries.forEach(p -> p.getFilterType().forEach(f -> {if (filterType.containsKey(f)) {Integer count = filterType.get(f); filterType.put(f, ++count);} else {filterType.put(f, 1);} }));
		for (String key: filterType.keySet()) {
			System.out.println(key + " : " + filterType.get(key));
		}
	}	
	
	public static void PrintStatisticsQueries(OutputStream os, List<Entry> entries, String queryType) {
		PrintWriter pw = new PrintWriter(os);
		Long queriesWfilter = entries.stream().filter(p -> (!p.filters.isEmpty())).count();
		Long queriesWclicks = entries.stream().filter(p -> (!p.clicks.isEmpty())).count();
		Long queriesWfilterclicks = entries.stream().filter(p -> (!p.filters.isEmpty() && !p.clicks.isEmpty())).count();
		Long queriesOnlyFilter = entries.stream().filter(p -> (!p.filters.isEmpty()) && (p.query.equals("") || p.query.equals("NO VALUE PROVIDED") || p.query.equals("*") || p.query.equals("*:*"))).count();
		List<Entry> userQueries = entries.stream().filter(p -> (!p.query.equals("NO VALUE PROVIDED") && !p.query.equals("*") && !p.query.equals("*:*"))).collect(Collectors.toList());
		
		pw.println("Type of queries: " + queryType);
		pw.println("Number of queries: " + entries.size());
		pw.println("*** Measures for evaluation report");
		pw.println("Percentage of queries with clicks (% all queries): " + (queriesWclicks / Double.valueOf(entries.size())) * 100);
		pw.println("Percentage of queries with filter (% all queries): " + (queriesWfilter / Double.valueOf(entries.size())) * 100);
		pw.println("Percentage of queries with filters that have clicks: " + (queriesWfilterclicks /  Double.valueOf(queriesWfilter)) * 100);
		pw.println("Percentage of queries only filter (% all queries): " + (queriesOnlyFilter / Double.valueOf(entries.size())) * 100);
		pw.println("Type of filters used and percentage of queries with filters where it has been used:");
		Map<String, Integer> filterType = new HashMap<String, Integer>();
		entries.forEach(p -> p.getFilterType().forEach(f -> {if (filterType.containsKey(f)) {Integer count = filterType.get(f); filterType.put(f, ++count);} else {filterType.put(f, 1);} }));
		Integer total = filterType.values().stream().mapToInt(p -> p).sum();
		for (String key: filterType.keySet()) {
			pw.println(key + " : " + (filterType.get(key) / Double.valueOf(total)) * 100);
		}

		pw.println();
		pw.println("*** Other measures");
		pw.println("Number of queries with no hits: " + entries.stream().filter(p -> p.getHits() == 0).count());
		pw.println("Number of queries with actual keywords (user queries): " + userQueries.size());
		pw.println("Number of queries with filter: " + queriesWfilter);
		pw.println("Number of queries with filter + clicks: " + queriesWfilterclicks);
		pw.println("Number of queries only filter: " + queriesOnlyFilter);
		pw.println("Number of queries keyword+filter: " + entries.stream().filter(p -> (!p.filters.isEmpty()) && (!p.query.equals("") && !p.query.equals("NO VALUE PROVIDED") && !p.query.equals("*") && !p.query.equals("*:*"))).count());
		//System.out.println("Number of queries keyword+filter: " + entries.stream().filter(p -> (!p.filters.isEmpty()) && (!p.query.equals("NO VALUE PROVIDED") && !p.query.equals("*") && !p.query.equals("*:*"))).count());
		pw.println("Number of queries with clicks: " + queriesWclicks);
		pw.println("Number of queries with clicks & only filter: " + entries.stream().filter(p -> (!p.clicks.isEmpty() && (!p.filters.isEmpty()) && (p.query.equals("") || p.query.equals("NO VALUE PROVIDED") || p.query.equals("*") || p.query.equals("*:*")))).count());
		pw.println("Number of queries with clicks & keyword+filter: " + entries.stream().filter(p -> (!p.clicks.isEmpty() && (!p.filters.isEmpty()) && (!p.query.equals("") && !p.query.equals("NO VALUE PROVIDED") && !p.query.equals("*") && !p.query.equals("*:*")))).count());
		pw.println("Average number of sessions per query: " + entries.stream().mapToDouble(p -> (p.clicks.keySet().size())).average());
		pw.println("Max. sessions per query: " + entries.stream().mapToDouble(p -> (p.clicks.keySet().size())).max());
		pw.println("Average clicks per query/session: " + entries.stream().flatMap(p -> (p.clicks.values().stream())).mapToDouble(p -> (p.size())).average());
		pw.println();
		pw.close();
	}
	
	private static void printQrel(List<Entry> entries, OutputStream os) {
		PrintWriter pw = new PrintWriter(os);
		
		for (Entry e: entries.stream().filter(p -> (!p.clicks.isEmpty())).collect(Collectors.toList())) {
			for (String doc:e.getIdsClicked().keySet()) {
				pw.write(e.hashCode() + " " + "Logs" + " " + doc + " " + "1"  + "\n");
			}
		}
		pw.close();
	}
	
	private static void printResults(List<Entry> entries, OutputStream os) {
		PrintWriter pw = new PrintWriter(os);
		for (Entry e: entries.stream().filter(p -> (!p.clicks.isEmpty())).collect(Collectors.toList())) {
			Integer maxRank = 0;
			maxRank = Collections.max(e.getIdsClicked().values());
			for (int i = 1; i <= maxRank; i++) {
				if (!e.getIdsClicked().values().contains(i)) {
					Double score = (maxRank / Double.valueOf(i)) / maxRank;
					pw.write(e.hashCode() + " " + "Logs" + " " + i + " " + e.hashCode()+"-"+ i + " " + score +  " " + "Logs" + "\n");
				}
			}
			for (String doc:e.getIdsClicked().keySet()) {
				Integer rank = e.getIdsClicked().get(doc);
				Double score = (maxRank / Double.valueOf(rank)) / maxRank;
				pw.write(e.hashCode() + " " + "Logs" + " " + doc + " " + e.getIdsClicked().get(doc) + " " + score +  " " + "Logs" + "\n");
			}
			
		}
		pw.close();
	}
	
	public static void printTRECfiles(List<Entry> entries, OutputStream qrelOs, OutputStream resOs) {
		printQrel(entries, qrelOs);
		printResults(entries, resOs);
	}
	

	public static void main(String[] args) throws IOException {
		try {
			System.out.println("Processing...");
			InputStream is = Process.class.getClassLoader().getResourceAsStream("resources/log4j.properties");
			PropertyConfigurator.configure(is);
			Properties prop;
			prop = Utils.readProperties(Process.class.getClassLoader().getResourceAsStream("resources/config.properties"));
			Path data = Paths.get(prop.getProperty("path"));
			List<Entry> entries = ImportEntries(data);
			//entries = entries.stream().filter(p -> p.getHits() > 0).collect(Collectors.toList());
			List<Entry> queriesWkeywords = entries.stream().filter(p -> (!p.query.equals("") && !p.query.equals("NO VALUE PROVIDED") && !p.query.equals("*") && !p.query.equals("*:*"))).collect(Collectors.toList());
			List<Entry> queriesOnlyFilter = entries.stream().filter(p -> ((p.query.equals("") || p.query.equals("NO VALUE PROVIDED") || p.query.equals("*") || p.query.equals("*:*")))).collect(Collectors.toList());

			OutputStream stats = new FileOutputStream("stats_all.txt");
			PrintStatisticsQueries(stats, entries, "All queries");
			stats.close();
			stats = new FileOutputStream("stats_keywords.txt");
			PrintStatisticsQueries(stats, queriesWkeywords, "Only queries with keywords different from '*' or '*:*' (not only filters)");
			stats.close();
			stats = new FileOutputStream("stats_filters.txt");
			PrintStatisticsQueries(stats, queriesOnlyFilter, "Only queries with filters (or where query is '*' or '*:*')");
			stats.close();
			//List<Session> session = ImportSessions(data);
			//PrintStatisticsSessions(session);
			OutputStream qrel = new FileOutputStream("qrel_all.txt");
			OutputStream res = new FileOutputStream("res_all.txt");
			printTRECfiles(entries, qrel, res);
			qrel.close();
			res.close();
			qrel = new FileOutputStream("qrel_keywords.txt");
			res = new FileOutputStream("res_keywords.txt");
			printTRECfiles(queriesWkeywords, qrel, res);
			qrel.close();
			res.close(); 
			qrel = new FileOutputStream("qrel_filters.txt");
			res = new FileOutputStream("res_filters.txt");
			printTRECfiles(queriesOnlyFilter, qrel, res);
			qrel.close();
			res.close();
			System.out.println("Stats and TREC files generated");
		} catch (IOException e) {
			logger.fatal(e.getMessage());
			throw e;
		}
	}

}
