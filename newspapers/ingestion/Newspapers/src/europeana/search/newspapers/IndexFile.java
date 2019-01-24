package europeana.search.newspapers;

import java.io.IOException;
import java.io.InputStream;
import java.util.Collection;
import java.util.HashSet;
import java.util.List;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;

import javax.xml.namespace.QName;
import javax.xml.stream.XMLInputFactory;
import javax.xml.stream.XMLStreamException;
import javax.xml.stream.XMLStreamReader;

import org.apache.log4j.Logger;
import org.apache.solr.client.solrj.SolrClient;
import org.apache.solr.client.solrj.SolrQuery;
import org.apache.solr.client.solrj.SolrServerException;
import org.apache.solr.client.solrj.response.QueryResponse;
import org.apache.solr.common.SolrDocument;
import org.apache.solr.common.SolrInputDocument;
import org.apache.solr.common.SolrInputField;

import com.ctc.wstx.api.WstxInputProperties;

import europeana.utils.Buffer;
import europeana.utils.SolrErrorHandling;

public class IndexFile implements Runnable {
	static Logger logger = Logger.getLogger(IndexFile.class);
	
	ZipFile zipFile = null;
	Buffer<SolrInputDocument> buffer = null;
	ZipEntry entry = null;
	SolrClient indexClient;
	SolrClient queryClient;
	String queryCollection;
	HashSet<String> nvfields;
	HashSet<String> supplangs;
	
	
	public IndexFile(ZipFile zipFile, ZipEntry entry, Buffer<SolrInputDocument> buffer, SolrClient indexClient, SolrClient queryClient, String queryCollection, HashSet<String> nvfields, HashSet<String> supplangs) {
		this.zipFile = zipFile;
		this.entry = entry;
		this.buffer = buffer;
		this.indexClient = indexClient;
		this.queryClient = queryClient;
		this.nvfields = nvfields;
		this.supplangs = supplangs;
		this.queryCollection = queryCollection;
	}

	@Override
	public void run() {
		try {
			InputStream stream = zipFile.getInputStream(entry);
			logger.debug("Processing document " + zipFile.getName() + "." + entry.getName());
			SolrInputDocument ftDocument = GetFulltextDoc(stream, supplangs);
			SolrDocument metadataDocument = GetMetadataDoc(queryClient, queryCollection, ftDocument.getFieldValue("europeana_id").toString());
			SolrInputDocument mergeDocument = Merge(ftDocument, metadataDocument, nvfields);
			synchronized(this) {
				buffer.Add(mergeDocument);
				if (buffer.isFull()) {
					List<SolrInputDocument> toindex = buffer.Retrieve();
					if (!toindex.isEmpty()) {
						indexClient.add(toindex);
						//SolrErrorHandling.Commit(solrIndex); //This is already done automatically according to the Solr configuration in solrconfig.xml
						logger.info("Indexed documents file " + zipFile.getName()+ " - batch "+ buffer.GetItemsBuffered() / buffer.GetCapacity() + " - Total documents indexed: " + buffer.GetItemsBuffered());
					}
				}
			}
			stream.close();
			logger.debug("Processed document " + zipFile.getName() + "." + entry.getName());
		} catch (SolrServerException e) {
			logger.error("Solr Server Exception: "+zipFile.getName() + "." + entry.getName() + " - " + e.getMessage());
			e.printStackTrace();
		} catch (XMLStreamException e) {
			logger.error("XML Stream Exception: "+zipFile.getName() + "." + entry.getName() + " - " + e.getMessage());
			e.printStackTrace();
		} catch (IllegalArgumentException e) {
			logger.error("Malformed XML file: "+zipFile.getName() + "." + entry.getName() + " - " + e.getMessage());
			e.printStackTrace();
		} catch (IOException e) {
			logger.error("IO error: "+zipFile.getName() + "." + entry.getName() + " - " + e.getMessage());
			e.printStackTrace();
		}
	}
	
	private static SolrDocument GetMetadataDoc(SolrClient queryClient, String queryCollection, String europeana_id) throws SolrServerException, IOException {
		SolrQuery query = new SolrQuery();
		query.setQuery("europeana_id"+":"+"\""+europeana_id + "\"");
		QueryResponse response = null;
		response = SolrErrorHandling.Query(queryClient, queryCollection, query);
		if (response.getResults().size() != 1) {
			throw new IllegalArgumentException("Metadata index in production contains " + response.getResults().size() + " metadata records for id " + europeana_id);
		}
		return response.getResults().get(0);
	}
	

	private static SolrInputDocument Merge(SolrInputDocument ftDocument, SolrDocument metadataDocument, HashSet<String> nvfields) {
		metadataDocument.forEach(p -> {
			if (!ftDocument.containsKey(p.getKey())) {
				if (!nvfields.contains(p.getKey().toString())){
						ftDocument.addField(p.getKey(), p.getValue());
				}
			}
		});
		ftDocument.setField("_version_", 0);
		ftDocument.setField("is_fulltext", true);
		Collection<Object> issued_dates = metadataDocument.getFieldValues("proxy_dcterms_issued");
		ftDocument.setField("issued", issued_dates);
		SolrInputField datesRange = new SolrInputField("datesRange");
		for (Object d: issued_dates) {
			datesRange.addValue(d.toString(),  1.0F);
		}
		ftDocument.setField("issued_range", datesRange);		
		return ftDocument;
	}
	
	private static SolrInputDocument GetFulltextDoc(InputStream stream, HashSet<String> supplangs) throws IllegalArgumentException, XMLStreamException{
		XMLInputFactory xmlInputFactory = XMLInputFactory.newInstance();
		xmlInputFactory.setProperty(XMLInputFactory.IS_COALESCING, Boolean.TRUE);
		xmlInputFactory.setProperty(WstxInputProperties.P_MAX_ENTITY_COUNT, Integer.valueOf(50000000));
		XMLStreamReader xmlStreamReader = xmlInputFactory.createXMLStreamReader(stream);
		SolrInputDocument document = new SolrInputDocument();
		String xmlbase = null;
		String fulltext = null;
		String language ="";
		boolean ftElement = false;
		boolean valElement = false;
		boolean langElement = false;
		while (xmlStreamReader.hasNext()) {
		  int eventType = xmlStreamReader.next();
		  switch (eventType) {
		  case XMLStreamReader.START_ELEMENT:
		        QName qName = xmlStreamReader.getName();
		        switch (qName.getLocalPart()) {
		        case "RDF": xmlbase = xmlStreamReader.getAttributeValue("http://www.w3.org/XML/1998/namespace", "base"); ftElement = false; valElement = false; langElement = false; break;
		        case "FullTextResource": ftElement = true; valElement = false; langElement = false; break;
		        case "language": if (ftElement && qName.getNamespaceURI().equals("http://purl.org/dc/elements/1.1/")) langElement = true; valElement = false; break;
		        case "value": if (ftElement && qName.getNamespaceURI().equals("http://www.w3.org/1999/02/22-rdf-syntax-ns#")) valElement = true; langElement = false; break;
		        default: ftElement = false; valElement = false; langElement = false;
		        }
		        break;
		  case XMLStreamReader.CHARACTERS: if (langElement) language = xmlStreamReader.getText(); else if (valElement)  fulltext = xmlStreamReader.getText(); break;
		  default: valElement = false; langElement = false;
		  }
		}
		
		if (xmlbase == null || !xmlbase.contains("http://data.europeana.eu/annotation")) {
			throw new IllegalArgumentException("'xml:base' attribute is lacking or malformed in xml file. Content of attribute: "+xmlbase);
		} 
		String europeana_id = xmlbase.replace("http://data.europeana.eu/annotation", "");
		document.addField("europeana_id", europeana_id);
		if (fulltext != null) {
			if (supplangs.contains(language)) {
				document.addField("fulltext."+language, fulltext);
			} else { //if the language tag contains generic-specific language, check the specific, then the generic, and if neither of them exists in the schema, index with the generic field for any language
				String glang = language.replaceAll("-.*$", "");
				if (supplangs.contains(glang)) {
					document.addField("fulltext."+glang, fulltext);
				} else {
					document.addField("fulltext.", fulltext); //undefined language
					logger.warn("Fulltext language '"+ language +"' not found. Indexed with general analyzer in field 'fulltext.'.");
				}
			}
		}
		return document;
	}


}
