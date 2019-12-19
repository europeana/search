import unittest
import entities.HarvesterConfig

class ConfigTest(unittest.TestCase):
    
    def test_harvester_config(self):
        config = entities.HarvesterConfig.HarvesterConfig()
        print('mongo host: ' + config.get_mongo_host())
        print('mongo port: ' + str(config.get_mongo_port()))
        print('organization mongo host: ' + config.get_mongo_host('organization'))