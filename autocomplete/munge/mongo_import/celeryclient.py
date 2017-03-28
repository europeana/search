from celery import group, chain
from tasks import build_concept_file, build_agent_file, get_concept_count, get_agent_count, get_place_count, build_place_file
import entities.ContextClassHarvesters
from entities.ContextClassHarvesters import ContextClassHarvester

chunk_size = entities.ContextClassHarvesters.ContextClassHarvester.CHUNK_SIZE

# we iterate through the total number of records
# building and indexing each file in turn
# TODO: add commit + optimize task to end of chord
#export_concepts = group( build_concept_file.s(i) for i in range(0, get_concept_count.delay().get(), chunk_size ))
#export_concepts()

export_agents = group(build_agent_file.s(i) for i in range(0, get_agent_count.delay().get(), chunk_size ))
export_agents()

export_places = group(build_place_file.s(i) for i in range(0, get_place_count.delay().get(), chunk_size ))
export_places()
