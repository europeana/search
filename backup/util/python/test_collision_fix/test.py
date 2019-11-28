import requests

SEARCH_API = "https://www.europeana.eu/api/v2/search.json?wskey=api2demo"
TEST_API = "https://alpha-api.cfapps.io/api/v2/search.json?wskey=api2demo"

test_entities = {

    61096 : {

        "http://data.europeana.eu/agent/base/61096" : "Giorgione",
        "http://viaf.org/viaf/61096" : "Bernardo Bellotto"

    },
    101818 : {

        "RM0001.PEOPLE.101818" : "Braquenié Frères",
        "http://data.europeana.eu/agent/base/101818" : "Pietro Lucatelli"

    }
}

# Scenarios to test

# Affected fields are proxy_dc_creator, proxy_dc_contributor, who

# Potentially affected fields are CREATOR, CONTRIBUTOR

# utility functions

def compare_label_results(test_field):
    errors = []
    for clash, clashers in test_entities.items():
        for id, label in clashers.items():
            qry = "&profile=minimal&query=" + test_field + ":\"" + label + "\""
            try:
                srch_res = requests.get(SEARCH_API + qry).json()
                test_res = requests.get(TEST_API + qry).json()
                srch_sum = [item['id'] for item in srch_res['items']]
                test_sum = [item['id'] for item in test_res['items']]
                if(set(srch_sum) != set(test_sum)):
                    errors.append(id)
            except Exception as e:
                print("Test string_search_unfield_reg failed to complete on entity " + str(id) + ": " + str(e))
    return errors

def compare_url_results(test_field):
    errors = []
    for clash, clashers in test_entities.items():
        for id, label in clashers.items():
            qry = "&profile=minimal&query=" + test_field + ":\"" + id + "\""
            try:
                srch_res = requests.get(SEARCH_API + qry).json()
                test_res = requests.get(TEST_API + qry).json()
                srch_sum = [item['id'] for item in srch_res['items']]
                test_sum = [item['id'] for item in test_res['items']]
                if(set(srch_sum) != set(test_sum)):
                    errors.append(id)
            except Exception as e:
                print("Test url_search_unfield_reg failed to complete on entity " + str(id) + ": " + str(e))
    return errors

def clash_exists_on_prod():
    found_errors = 0
    for clash, clashers in test_entities.items():
        for url in clashers.keys():
            txt_qry = "&profile=minimal&query=text:\"" + url + "\""
            who_qry = "&profile=minimal&query=who:\"" + url + "\""
            try:
                txt_cnt = requests.get(SEARCH_API + txt_qry).json()['totalResults']
                who_cnt = requests.get(SEARCH_API + who_qry).json()['totalResults']
                print("Text hits are " + str(txt_cnt) + " and who hits are " + str(who_cnt) + " on " + url)
                if(txt_cnt < who_cnt): found_errors += 1
            except:
                print("Could not complete clash confirmation on entity " + url)
                return False
    return found_errors > 0

def url_results_are_disjoint(field, provider_id, europeana_id):
    prov_qry = "&profile=minimal&query=" + field + ":\"" + provider_id + "\""
    eurp_qry = "&profile=minimal&query=" + field + ":\"" + europeana_id + "\""
    try:
        prov_resp = requests.get(TEST_API + prov_qry).json()
        eurp_resp = requests.get(TEST_API + eurp_qry).json()
        prov_res = [item['id'] for item in prov_resp['items']]
        eurp_res = [item['id'] for item in eurp_resp['items']]
    except Exception as e:
        print("Could not complete result contrast on field " + field + " with ids " + provider_id + ", " + europeana_id + ": " + str(e))
        return False
    prov_res = set(prov_res)
    eurp_res = set(eurp_res)
    return not(len(prov_res.intersection(eurp_res)))

# REGRESSION TESTS

# String-search on non-affected fields is unchanged

def reg_check_labels():
    errors = 0
    example_na_fields = ['text', 'title', 'subject']
    for field in example_na_fields:
        errors = compare_label_results(field)
        if(len(errors) == 0):
            print("All tests passed for reg_check_labels on field " + field)
        else:
            [print("Test reg_check_labels failed on field name " + field + " with entity \"" + err + "\"") for err in errors]
            errors += 1
    return (not(errors))
# URL-search on non-affected fields is unchanged

def reg_check_urls():
    errors = 0
    example_na_fields = ['text', 'title', 'subject']
    for field in example_na_fields:
        errors = compare_url_results(field)
        if(len(errors) == 0):
            print("All tests passed for reg_check_urls on field " + field)
        else:
            [print("reg_check_urls failed on field name " + field + " with entity \"" + err + "\"") for err in errors]
            errors += 1
    return (not(errors))
# String-search on affected fields is unchanged

def reg_affcheck_labels():
    errors = 0
    example_a_fields = ['proxy_dc_contributor', 'proxy_dc_creator', 'who']
    for field in example_a_fields:
        errors = compare_label_results(field)
        if(len(errors) == 0):
            print("All tests passed for reg_affcheck_labels on field " + field)
        else:
            [print("Test reg_affcheck_labels failed on field name " + field + " with entity \"" + err + "\"") for err in errors]
            errors += 1
    return (not(errors))
# URL-search on CONTRIBUTOR and CREATOR is unchanged

def reg_facheck_labels():
    errors = 0
    example_fac_fields = ['CREATOR', 'CONTRIBUTOR']
    for field in example_fac_fields:
        errors = compare_url_results(field)
        if(len(errors) == 0):
            print("All tests passed for reg_facheck_labels on field " + field)
        else:
            [print("Test reg_facheck_labels failed on field name " + field + " with entity \"" + err + "\"") for err in errors]
            errors += 1
    return (not(errors))
# ACTIVE TESTS

# Results for clashing identifiers are disjoint on who field
def who_is_disjoint():
    errors = []
    for clash, clashers in test_entities.items():
        clash_terms = list(clashers.keys())
        if(not(url_results_are_disjoint('who', clash_terms[0], clash_terms[1]))):
            errors.append(clash)
    if(len(errors) == 0):
        print("who_is_disjoint test PASSED")
        return True
    else:
        [print("who_is_disjoint test FAILED on identifiers for " + str(err)) for err in errors]
        return False
# Results for clashing identifiers are disjoint on creator field

def creator_is_disjoint():
    errors = []
    for clash, clashers in test_entities.items():
        clash_terms = list(clashers.keys())
        if(not(url_results_are_disjoint('proxy_dc_creator', clash_terms[0], clash_terms[1]))):
            errors.append(clash)
    if(len(errors) == 0):
        print("creator_is_disjoint test PASSED")
        return True
    else:
        [print("creator_is_disjoint test FAILED on identifiers for " + str(err)) for err in errors]
        return False

# Results for clashing identifiers are disjoint on contributor field
def contributor_is_disjoint():
    # only 61096 will have clashes here
    clash_terms = list(test_entities[61096].keys())
    if(url_results_are_disjoint('proxy_dc_contributor', clash_terms[0], clash_terms[1])):
        print("contributor_is_disjoint test PASSED")
        return True
    else:
        print("contributor_is_disjoint test FAILED")
        return False

def test_all():
    a = reg_check_labels()
    b = reg_check_urls()
    c = reg_affcheck_labels()
    d = reg_facheck_labels()
    e = creator_is_disjoint()
    f = contributor_is_disjoint()
    g = who_is_disjoint()
    if(a and b and c and d and e and f and g):
        print("Test suite PASSED")
    else:
        print("Test suite FAILED")

test_all()
