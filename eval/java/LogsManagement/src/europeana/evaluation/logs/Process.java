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
						if (!filters.isEmpty()) {
							try {
								JSONObject json_fil = new JSONObject(filters.replace("\\x00", " ").replace("\\xa0", " "));
								for (String key: json_fil.keySet()) {
									current.addFilterType(key);
								}
							} catch (JSONException e) {
								logger.warn("Error on session " + idSession + " filter: " + filters);
							}
						}
						
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
	
	public static void PrintStatisticsQueries(List<Entry> entries) {
		System.out.println("Number of queries: " + entries.size());
		
		List<Entry> userQueries = entries.stream().filter(p -> (!p.query.equals("NO VALUE PROVIDED") && !p.query.equals("*") && !p.query.equals("*:*"))).collect(Collectors.toList());
		System.out.println("Number of queries with actual keywords: " + userQueries.size());
		System.out.println("*** Statistics all the queries");
		System.out.println("Number of queries with filter: " + entries.stream().filter(p -> (!p.filters.isEmpty())).count());
		System.out.println("Number of queries only filter: " + entries.stream().filter(p -> (!p.filters.isEmpty()) && (p.query.equals("") || p.query.equals("NO VALUE PROVIDED") || p.query.equals("*") || p.query.equals("*:*"))).count());
		System.out.println("Number of queries keyword+filter: " + entries.stream().filter(p -> (!p.filters.isEmpty()) && (!p.query.equals("") && !p.query.equals("NO VALUE PROVIDED") && !p.query.equals("*") && !p.query.equals("*:*"))).count());
		//System.out.println("Number of queries keyword+filter: " + entries.stream().filter(p -> (!p.filters.isEmpty()) && (!p.query.equals("NO VALUE PROVIDED") && !p.query.equals("*") && !p.query.equals("*:*"))).count());
		System.out.println("Number of queries with clicks: " + entries.stream().filter(p -> (!p.clicks.isEmpty())).count());
		System.out.println("Number of queries with clicks & only filter: " + entries.stream().filter(p -> (!p.clicks.isEmpty() && (!p.filters.isEmpty()) && (p.query.equals("") || p.query.equals("NO VALUE PROVIDED") || p.query.equals("*") || p.query.equals("*:*")))).count());
		System.out.println("Number of queries with clicks & keyword+filter: " + entries.stream().filter(p -> (!p.clicks.isEmpty() && (!p.filters.isEmpty()) && (!p.query.equals("") && !p.query.equals("NO VALUE PROVIDED") && !p.query.equals("*") && !p.query.equals("*:*")))).count());
		System.out.println("Average number of sessions per query: " + entries.stream().mapToDouble(p -> (p.clicks.keySet().size())).average());
		System.out.println("Max. sessions per query: " + entries.stream().mapToDouble(p -> (p.clicks.keySet().size())).max());
		System.out.println("Average clicks per query/session: " + entries.stream().flatMap(p -> (p.clicks.values().stream())).mapToDouble(p -> (p.size())).average());
		
		System.out.println("*** Statistics user queries");
		System.out.println("Number of queries with filter: " + userQueries.stream().filter(p -> (!p.filters.isEmpty())).count());
		System.out.println("Number of queries with clicks: " + userQueries.stream().filter(p -> (!p.clicks.isEmpty())).count());
		System.out.println("Average number of sessions per query: " + userQueries.stream().mapToDouble(p -> (p.clicks.keySet().size())).average());
		System.out.println("Max. sessions per query: " + userQueries.stream().mapToDouble(p -> (p.clicks.keySet().size())).max());
		System.out.println("Average clicks per query/session: " + userQueries.stream().flatMap(p -> (p.clicks.values().stream())).mapToDouble(p -> (p.size())).average());
		
		List<Entry> withClicks = userQueries.stream().filter(p -> (!p.clicks.isEmpty())).collect(Collectors.toList());
		System.out.println("*** Statistics queries with clicks");
		System.out.println("Number of queries with filter: " + withClicks.stream().filter(p -> (!p.filters.isEmpty())).count());
		System.out.println("Average number of sessions per query: " + withClicks.stream().mapToDouble(p -> (p.clicks.keySet().size())).average());
		System.out.println("Max. sessions per query: " + withClicks.stream().mapToDouble(p -> (p.clicks.keySet().size())).max());
		System.out.println("Average clicks per query/session: " + withClicks.stream().flatMap(p -> (p.clicks.values().stream())).mapToDouble(p -> (p.size())).average());

	}
	
	private static void printQrel(List<Entry> entries, OutputStream os) {
		List<Entry> userQueriesClicked = entries.stream().filter(p -> (!p.query.equals("") && !p.query.equals("NO VALUE PROVIDED") && !p.query.equals("*") && !p.query.equals("*:*") && !p.clicks.isEmpty())).collect(Collectors.toList());
		PrintWriter pw = new PrintWriter(os);
		for (Entry e: userQueriesClicked) {
			for (String doc:e.getIdsClicked().keySet()) {
				pw.write(e.hashCode() + " " + "Logs" + " " + doc + " " + "1"  + "\n");
			}
		}
		pw.close();
	}
	
	private static void printResults(List<Entry> entries, OutputStream os) {
		List<Entry> userQueriesClicked = entries.stream().filter(p -> (!p.query.equals("") && !p.query.equals("NO VALUE PROVIDED") && !p.query.equals("*") && !p.query.equals("*:*") && !p.clicks.isEmpty())).collect(Collectors.toList());
		PrintWriter pw = new PrintWriter(os);
		
		for (Entry e: userQueriesClicked) {
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
		InputStream is = Process.class.getClassLoader().getResourceAsStream("log4j.properties");
		PropertyConfigurator.configure(is);
		Properties p;
			p = Utils.readProperties(Process.class.getClassLoader().getResourceAsStream("config.properties"));
			Path data = Paths.get(p.getProperty("path"));
			List<Entry> entries = ImportEntries(data);
			PrintStatisticsQueries(entries);
			List<Session> session = ImportSessions(data);
			PrintStatisticsSessions(session);
			OutputStream qrel = new FileOutputStream("qrel.txt");
			OutputStream res = new FileOutputStream("res.txt");
			printTRECfiles(entries, qrel, res);
			qrel.close();
			res.close();
		} catch (IOException e) {
			logger.fatal(e.getMessage());
			throw e;
		}
	}

}
