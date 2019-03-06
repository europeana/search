package europeana.utils;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import org.apache.solr.common.SolrInputDocument;

public class Buffer<T> {

	private List<T> buffer = new ArrayList<T>();
	private Integer maxCapacity;
	private Integer itemsBuffered;
	
	//TEST
	public Set<String> ids = new HashSet<String>();
	public int maxChars = 0;
	
	public Integer GetCapacity() {
		return maxCapacity;
	}
	
	public Integer GetItemsBuffered() {
		return itemsBuffered;
	}
	
	public Buffer(Integer maxCapacity) {
		this.maxCapacity = maxCapacity;
		this.itemsBuffered = 0;
	}
	
	synchronized public void Add(T item) {
		buffer.add(item);
		itemsBuffered++;
		
		//TEST
		SolrInputDocument d = (SolrInputDocument) item;
		ids.add(d.getField("europeana_id").toString());
//		for (Object lang : d.getFieldValues("LANGUAGE")) {
//			if (d.getFieldValue("fulltext." + lang.toString()) != null) {
//				int len = d.getFieldValue("fulltext." + lang.toString()).toString().length();
//				if (len > maxChars) maxChars = len; 
//			}
//		}
	}
	
	synchronized public List<T> Retrieve(){
		List<T> items = new ArrayList<T>(buffer);
		buffer.clear();
		return items;
	}
	
	synchronized public void Clear() {
		buffer.clear();
	}
	
	synchronized public Boolean isFull() {
		if (buffer.size() >= maxCapacity) {
			return true;
		}
		return false;
	}

	synchronized public Boolean isEmpty() {
		return buffer.isEmpty();
	}
}
