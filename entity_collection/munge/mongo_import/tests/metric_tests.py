import unittest
import ranking_metrics.RelevanceCounter

class MetricsTest(unittest.TestCase):
    
    def test_get_max_metrics(self):
        print('Agent max metrics ')
        amc = ranking_metrics.RelevanceCounter.AgentRelevanceCounter()
        agent_metrics = amc.get_max_metrics() 
        self.print_max_metrics(agent_metrics)
        
        print('Place max metrics ')
        pmc = ranking_metrics.RelevanceCounter.PlaceRelevanceCounter()
        place_metrics = pmc.get_max_metrics()
        self.print_max_metrics(place_metrics)
        
        print('Concept max metrics ')
        cmc = ranking_metrics.RelevanceCounter.ConceptRelevanceCounter()
        concept_metrics = cmc.get_max_metrics()
        self.print_max_metrics(concept_metrics)
        
        print('Organization max metrics ')
        omc = ranking_metrics.RelevanceCounter.OrganizationRelevanceCounter()
        organization_metrics = omc.get_max_metrics()
        self.print_max_metrics(organization_metrics)
    
    def test_get_max_pagerank(self):
        print('Agent max pagerank')
        amc = ranking_metrics.RelevanceCounter.AgentRelevanceCounter()
        agent_metrics = amc.get_max_pagerank() 
        self.print_max_metrics(agent_metrics)
        
        print('Place max pagerank ')
        pmc = ranking_metrics.RelevanceCounter.PlaceRelevanceCounter()
        place_metrics = pmc.get_max_pagerank()
        self.print_max_metrics(place_metrics)
        
        print('Concept max pagerank ')
        cmc = ranking_metrics.RelevanceCounter.ConceptRelevanceCounter()
        concept_metrics = cmc.get_max_pagerank()
        self.print_max_metrics(concept_metrics)
        
        print('Organization max pagerank ')
        omc = ranking_metrics.RelevanceCounter.OrganizationRelevanceCounter()
        organization_metrics = omc.get_max_pagerank()
        self.print_max_metrics(organization_metrics)
            
    def print_max_metrics(self, metrics):
        for metric, value in metrics.items():
            print(metric + ": " + str(value))    