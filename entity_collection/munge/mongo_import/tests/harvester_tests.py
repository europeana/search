# ========================================================================#
#
# Tests to ensure import process has run correctly.
#
# Note the scope of these tests: they test only that the import process
# is yielding the expected output. They do nothing to validate the
# data of the imported entities itself.
#
#=========================================================================#
import sys
import unittest
import entities.ContextClassHarvesters
import entities.preview_builder.PreviewBuilder

class HarvesterTest(unittest.TestCase):
   
    # tests on a couple of entities of each type
    def test_transform(self):
        ieb = entities.ContextClassHarvesters.IndividualEntityBuilder()
        test_entities = [
            "http://data.europeana.eu/agent/base/11241",   # Paris Hilton
            "http://data.europeana.eu/agent/base/146741",  # Leonardo da Vinci
            "http://data.europeana.eu/place/base/40360",   # Den Haag
            "http://data.europeana.eu/place/base/143914",  # Ferrara
            #"http://data.europeana.eu/concept/base/214",   # Neoclassicism
            "http://data.europeana.eu/concept/base/207",    # Byzantine art
            "http://data.europeana.eu/organization/1482250000002112001",    # BnF 
            "http://data.europeana.eu/organization/1482250000004375509", #Deutsches film institute
            "http://data.europeana.eu/agent/base/178", #agent max page rank: Aristotel
            "http://data.europeana.eu/place/base/216254", #place max page rank: United States
            "http://data.europeana.eu/concept/base/83", #concept max page rank: World War I
            "http://data.europeana.eu/organization/1482250000004505021", #organization max page rank: Internet Archive
        ]
        for test_entity in test_entities:
            print("building entity: " + test_entity)
            ieb.build_individual_entity(test_entity, is_test=True)
        #errors = test_files_against_mongo('dynamic')
        #errors.extend(test_json_formation('dynamic'))
        #return errors
        
    # tests on a couple of entities of each type
    def test_build_bnf_preview(self):
        #bnf
        #entity_id = "http://data.europeana.eu/organization/1482250000002112001"
        #government of catalunia
        entity_id = "http://data.europeana.eu/organization/1482250000004503580"
        ieb = entities.ContextClassHarvesters.IndividualEntityBuilder()
        ieb.build_individual_entity(entity_id, is_test=True)
      
        