# Evaluation

## Phase 1 (2016-06-28)

### Testbed

In the absence of clickstream logs, it was decided to base evaluation around a 50-item list of entities selected from the Europeana Best Bets - that is to say, entities that have already been manually identified as being of central cultural importance, and which should accordingly appear at or near the top of any suggestion list.

The basis of selection was to achieve wide coverage, with disparate media, time periods, and places being covered. For instance, it was important to make sure that not just artists, but writers, musicians, and other categories of person were also represented; and that geographical queries be available for every level from particular buildings to entire countries.

### Responsiveness

It is extremely important that autosuggest be _fast_ : users need the suggestions to appear as they type, not afterwards.

For each of the test items, a substring of between 3-6 characters was automatically generated to test with. The reason for this length is two-fold:

* autocomplete is not triggered by Solr until at least 3 characters have been entered
* at >6 characters, many entities are already complete (their labels are 6 characters or less long), while many others will be fully disambiguated - that is to say, there will be only one possible match. 3-6 characters is thus the length of maximal user utility

This string was then looped through to test the responsiveness of the Solr server - that is to say, if the five-character string 'Peter' was used for testing, the strings 'Pet', 'Pete', and 'Peter' were submitted in sequence, simulating the behaviour of a user engaged in autocomplete querying. The time taken for each response was recorded, and an average derived - in this case, of 192ms.

### Ranking

For each item in the testbed, an ID was determined. The 3-6 character substring for each item generated during responsiveness testing was then used to query the Entity Collection, and the position of the item's ID in the suggest response logged. Cases in which the item failed to appear scored 0. The nDCG of the response was then calculated, and an average calculated across the testbed.

This resulted in an average nDCG of 0.41. For comparison, nDCG for Europeana Collections as a whole is roughly 0.22.

One immediate means of improving this number would be to improve accent-handling: Individuals such as Paul Cézanne were not found because current processing retains diacritics that should be eliminated for ease of querying.

It should also be noted that ranking was sometimes adversely affected by name-order: while a search for 'Pic' still finds 'Pablo Picasso', infix-matches rank lower than prefix-matches, so that a record titled 'Picabia, Francis' would rank higher despite Picasso's higher absolute relevance.

#### A note on nDCG calculation

For this implementation, we are interested only if the single correct item for the request is present as close to the top of the result list as possible. Relevance is therefore binary, and summing of relevance is not an issue under these conditions, ndcg reduces to 1/log2(p), where p is the rank position of the item. 




