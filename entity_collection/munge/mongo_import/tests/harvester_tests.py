# ========================================================================#
#
# Tests to ensure import process has run correctly.
#
# Note the scope of these tests: they test only that the import process
# is yielding the expected output. They do nothing to validate the
# data of the imported entities itself.
#
#=========================================================================#

import unittest
import requests, json, os, sys, re, time
from pymongo import MongoClient
import entities.ContextClassHarvesters
import entities.preview_builder.PreviewBuilder

class HarvesterTest(unittest.TestCase):
   
    # tests on a couple of entities of each type
    def test_transform(self):
        ieb = entities.ContextClassHarvesters.IndividualEntityBuilder()
        test_entities = [
             "http://data.europeana.eu/agent/base/11241",   # Paris Hilton
             "http://data.europeana.eu/agent/base/146741",  # Leonardo da Vinci
             "http://data.europeana.eu/place/base/40361",   # Den Haag
             "http://data.europeana.eu/place/base/143914",  # Ferrara
             "http://data.europeana.eu/concept/base/214",   # Neoclassicism
             "http://data.europeana.eu/concept/base/207"    # Byzantine art
        ]
        for test_entity in test_entities:
            #ieb.build_individual_entity(test_entity, is_test=True)
            print("Entity uri: " + test_entity)

    # tests on a couple of entities of each type
    def test_build_bnf_preview(self):
        bnf_id = "http://data.europeana.eu/organization/1482250000002112001"
        #pb = entities.preview_builder.PreviewBuilder()
        ieb = entities.ContextClassHarvesters.IndividualEntityBuilder()
        ieb.build_individual_entity(bnf_id, is_test=True)
      
