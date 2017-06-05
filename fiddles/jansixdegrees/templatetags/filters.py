from django import template
import re

register = template.Library()

@register.filter(name='as_id')
def as_id(value):
    return value.split('/')[-1]

@register.filter(name='as_eurl')
def as_eurl(value):
    value = value.replace("http:/data.europeana.eu/item", "http://www.europeana.eu/portal/record")
    value = value + ".html"
    value = value.replace(".html.html", ".html")
    return value

@register.filter(name='as_phrase_search')
def as_phrase_search(value):
    value = re.sub("^\"", "", value)
    value = re.sub("\"$", "", value)
    value = re.sub("who:", "", value)
    value = value.replace("'", "\"")
    return value

@register.filter(name='as_year')
def as_year(value):
    try:
        year = value.split("-")[0].strip()
        return year
    except:
        return "?"

@register.filter(name='joinlist')
def joinlist(value):
    vals = [w.pref_label.capitalize() for w in value]
    vals = set(vals)
    vals = sorted(vals)
    return ", ".join(vals)

@register.filter(name='friendly_relations')
def friendly_relations(value):
    frels = dict()
    frels = {
            "employer" : "employed by",
            "child" : "has child",
            "father" : "father is",
            "mother" : "mother is",
            "spouse" : "married to",
            "student" : "has as student",
            "sister" : "sister is",
            "brother" : "brother is",
            "relative" : "relative of",
            "partner" : "partner of"
    }
    friendly_relation = value
    try:
        friendly_relation = frels[value]
    except:
        pass
    return friendly_relation
