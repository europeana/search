from celery import group, chain
from df_tasks import *

# all_places = get_all_places()
# we iterate through the total number of records
# building and indexing each file in turn
# TODO: add commit + optimize task to end of chord
# export_concepts = group(chain( build_concept_file.s(i) | index_file.s() ) for i in range(0, get_count.delay().get(), chunk_size ))
# export_concepts()

# eu_counts = group(chain( build_solr_qs.s(place) | get_df.s())  for place in all_places  )
# eu_counts()

#  export_agents = group(build_agent_file.s(i) for i in range(0, get_agent_count.delay().get(), chunk_size ))
#  export_agents()

all_places = get_unique_place_ids()
wkpd_counts = group(chain( get_place_records.s(place) | get_wpedia_hit_counts.s().set(countdown=0.1) | write_wpedia_hits.s()  ) for place in all_places)
wkpd_counts()