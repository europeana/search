package europeana.utils;

import java.io.IOException;
import java.io.InputStreamReader;
import java.net.URL;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.Map;

import javax.net.ssl.HttpsURLConnection;

import org.apache.commons.io.IOUtils;
import org.apache.commons.math3.util.Pair;
import org.apache.log4j.Logger;
import org.json.JSONObject;

public class APIErrorHandling {
	
	static Logger logger = Logger.getLogger(APIErrorHandling.class);
	public static final Integer ATTEMPTS = 3;
	public static final Long SLEEP_MS = 1000l;
	//public static final String SEARCH_URL = "https://www.europeana.eu/api/v2/search.json";
	public static final String KEY = "api2demo";
	public static final String REDIRECTION_URL = "https://www.europeana.eu/api/v2/record"; //9060/8E4E27037C8A531D568687FEEF00F7AB7C931090.json?wskey=api2demo"
	
	public static Pair<Integer, JSONObject> RedirectionQuery(String europeana_id) throws IOException{
		int attempts = ATTEMPTS;
		while (attempts > 0) {
			try {
				StringBuffer sb = new StringBuffer();
				sb.append("wskey=" + URLEncoder.encode(KEY, StandardCharsets.UTF_8.name()));
				URL request = new URL(REDIRECTION_URL.toString() + europeana_id + ".json?" + sb.toString());
				HttpsURLConnection con = (HttpsURLConnection)request.openConnection();
				Integer resCode = con.getResponseCode();
				JSONObject content = null;
				if (resCode == 200) {
					InputStreamReader is;
					is = new InputStreamReader(con.getInputStream());
					String text = IOUtils.toString(is);
					content = new JSONObject(text);
				}
				Pair<Integer, JSONObject> result = new Pair<Integer, JSONObject>(resCode, content);
			    return result;
			} catch (IOException e) {
				attempts--;
				if (attempts <= 0) {
					throw e;
				}
				try {
					Thread.sleep(SLEEP_MS);
				} catch (InterruptedException e1) {
					logger.warn("Redirection Query Attempt " + (ATTEMPTS - attempts) + " - Thread interrupted");
				}
			}
		}
		return null;
	}
	
	public static JSONObject SearchQuery(URL search_url, Map<String, String> params) throws IOException {
		int attempts = ATTEMPTS;
		while (attempts > 0) {
			try {
				StringBuffer sb = new StringBuffer();
				for (Map.Entry<String, String> p : params.entrySet()) {
					sb.append(p.getKey() + "=");
					sb.append(URLEncoder.encode(p.getValue(), StandardCharsets.UTF_8.name()));
					sb.append("&");
				}
				sb.append("wskey=" + URLEncoder.encode(KEY, StandardCharsets.UTF_8.name()));
				URL request = new URL(search_url.toString() + "?" + sb.toString());
				HttpsURLConnection con = (HttpsURLConnection)request.openConnection();
				Integer resCode = con.getResponseCode();
				JSONObject content = null;
				if (resCode == 200) {
					InputStreamReader is;
					is = new InputStreamReader(con.getInputStream());
					String text = IOUtils.toString(is);
					content = new JSONObject(text);
				}
				if (resCode != 200 || content == null || !content.getBoolean("success")) {
					throw new IOException("Search API error " +  resCode);
				}
			    return content;
			} catch (IOException e) {
				attempts--;
				if (attempts <= 0) {
					throw e;
				}
				try {
					Thread.sleep(SLEEP_MS);
				} catch (InterruptedException e1) {
					logger.warn("Search Query Attempt " + (ATTEMPTS - attempts) + " - Thread interrupted");
				}
			}
		}
		return null;
	}


}
