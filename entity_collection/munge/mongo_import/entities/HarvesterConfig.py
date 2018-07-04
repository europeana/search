class HarvesterConfig:
    
    import os
    
    DEFAULT_CONFIG_SECTION = 'CONFIG'
    HARVESTER_MONGO_HOST = 'harvester.mongo.host'
    HARVESTER_MONGO_PORT = 'harvester.mongo.port'
    HARVESTER_RELEVANCE_SOLR_URI = 'harvester.relevance.solr.core.uri'
    
    CONFIG_DIR = os.path.join(os.path.dirname(__file__), '..', 'config')
    
    
    def __init__(self):
        
        from configparser import RawConfigParser 
        
        self.config_file = HarvesterConfig.CONFIG_DIR + "/harvester.properties"
        self.config = RawConfigParser()
        self.config.read(self.config_file)
        
    def get_mongo_host (self, harvester_name = None):
        key = self.build_key(HarvesterConfig.HARVESTER_MONGO_HOST, harvester_name)
        return self.config.get(HarvesterConfig.DEFAULT_CONFIG_SECTION, key)
        
    def get_mongo_port (self, harvester_name = None):
        key = self.build_key(HarvesterConfig.HARVESTER_MONGO_PORT, harvester_name)
        return self.config.getint(HarvesterConfig.DEFAULT_CONFIG_SECTION, key)
    
    def get_relevance_solr (self):
        key = HarvesterConfig.HARVESTER_RELEVANCE_SOLR_URI
        return self.config.get(HarvesterConfig.DEFAULT_CONFIG_SECTION, key)
        
    def build_key (self, default_key, harvester_name = None):    
        if(harvester_name is None):
            return default_key
        else:
            return harvester_name + '.' + default_key 
        