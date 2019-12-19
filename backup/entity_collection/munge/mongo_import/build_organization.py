import sys
from entities.ContextClassHarvesters import IndividualEntityBuilder
entityBuilder = IndividualEntityBuilder()

if (len(sys.argv) >= 2):
    print("sys.argv: " + str(sys.argv))
    entityId = sys.argv[len(sys.argv) -1]
    solrDocFile = entityBuilder.build_individual_entity(sys.argv[1])
    print("generated: " + solrDocFile)
    
    