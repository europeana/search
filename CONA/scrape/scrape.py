from bs4 import BeautifulSoup
import re
import requests

DOMAIN = "http://www.getty.edu/cona/"
DESCRIPTION = re.compile("^CONAFullSubject.aspx\?subid=([\d]{9,})$")
ALPHA_UNFOLD = re.compile("^CONAHierarchy.aspx\?subid=([\d]{9,})&alpha=[A-Z0-9]$")
WRITE_DIR = "../munge/raw/"

def is_cona_link(tag):
    return tag.has_attr("href") and re.compile("^CONA").search(tag["href"])

def is_cona_subject_link(tag):
    return tag.has_attr("href") and re.compile(DESCRIPTION).search(tag["href"])

top_url = DOMAIN + "CONAHierarchy.aspx?subid=700000000&alpha="
top_page = requests.get(top_url)
top_soup = BeautifulSoup(top_page.content)
top_anchors = top_soup.find_all(is_cona_link)
top_links = [anchor["href"] for anchor in top_anchors]

facets = {}
mid_links = []
topics_to_facets = {}

# first we populate the facet descriptions
# this allows us to start the process at an arbitrary point
# and be assured we have all required values

for top_link in top_links:
    facet_match = DESCRIPTION.match(top_link)
    if(facet_match != None):
        url = DOMAIN + top_link
        page = requests.get(url)
        soup = BeautifulSoup(page.content)
        pref_term = soup.find(id='TablePrefTerm').tr.td.b.text
        facet_id = facet_match.group(1)
        facets[facet_id] = pref_term

# Now we go through and unfold each alphabetical heading
# retrieving the child links

for top_link in top_links:
    unfold_match = ALPHA_UNFOLD.match(top_link)
    if(unfold_match != None):
        url = DOMAIN + top_link
        page = requests.get(url)
        soup = BeautifulSoup(page.content)
        topic_id = unfold_match.group(1)
        for subject_link in soup.find_all(is_cona_subject_link):
            mid_links.append(subject_link["href"])
            topics_to_facets[subject_link["href"]] = topic_id

for mid_link in mid_links:
    url = DOMAIN + mid_link
    page = requests.get(url)
    soup = BeautifulSoup(page.content)
    # we don't need the <head> section
    soup.head.decompose()
    # img and script tags are often blowing the XML
    # well-formedness of the page, so we strip them out
    for img in soup.find_all("img"):
        img.decompose()
    for script in soup.find_all("script"):
        script.\
            decompose()
    page_facet = facets[topics_to_facets[mid_link]]
    facet_tag = soup.new_tag("span")
    facet_tag['class' \
              ''] = "CONA_facet"
    facet_tag.string = page_facet
    soup.body.insert(0,facet_tag)
    pretty_soup = soup.prettify()
    # the following path should give us the page title
    title = "" if soup.find(id='TablePrefTerm') == None else soup.find(id='TablePrefTerm').tr.td.b.text.lower()
    title = re.sub("[^\w\s]", "", title)
    title = re.sub(" ", "_", title)
    # however, sometimes the title is missing entirely
    # or a description has been entered into the title field
    file_name = title + ".xml" if (len(title) < 100 and title != "") else DESCRIPTION.match(mid_link).group(1) + ".xml"
    write_path = WRITE_DIR + file_name
    f = open(write_path, 'w')
    f.write(pretty_soup)
    f.close()

print("Complete!")




