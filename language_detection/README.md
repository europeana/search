# Language Detection Overview

This directory contains scripts and data for simple experimentation with applying language detection to our workflow.

## Iteration One - EuropeanaConnect core languages and Solr LangDetect

This is a preliminary pass at language identification over a corpus small enough to be checked cursorily by hand.

For each of the EuropeanaConnect core languages (German, English, Spanish, French, Italian, and Polish) an attempt was made to harvest 50 documents from our collections.  Sampling was done by retrieving 5 documents 10 times at intervals of 10000 documents (harvesting over the entire range of available documents placed an undue load on the Solr servers). Targeting metadata language was in fact fairly difficult - I queried by country of origin and by language of item, which was not entirely reliable - and thus ended up by my estimate with 58 English-language records, 46 French records, 46 German records, and 50 of the other languages. However, I deemed this sufficient for preliminary testing purposes.

The language detection task was complicated by the fact that the metadata is in some cases multilingual, a factor not taken into account. This led to the misidentification of 11 records.

Other common causes of misidentification were:

* No description being provided (6 misidentifications)
* Identical title and description (11 misidentifications)
* Titles and descriptions consisting entirely or chiefly of named entities, which don't really have a language as such (3 misidentications)

In addition, automated language detection works better the greater the quantity of data that it is fed; all misidentifications occurred on extremely short values. Even so, the overall accuracy of identification was 89%, providing a promising basis for further investigation.

A spreadsheet summarising the above can be found at [https://github.com/europeana/search/tree/master/language_detection/iteration_1/samples/detection_results.csv](https://github.com/europeana/search/tree/master/language_detection/iteration_1/samples/detection_results.csv). The test corpus can be found here: [https://github.com/europeana/search/tree/master/language_detection/iteration_1/samples].

For those with access to the R&D server, the Solr core can be found here: [http://144.76.218.178:8080/solr/#/langdetect]. The 'targetlang' field indicates the language of the document (though note the mistagging of 8 en documents as fr or de, as discussed above); the 'parsedlangs' field indicates the detected language.