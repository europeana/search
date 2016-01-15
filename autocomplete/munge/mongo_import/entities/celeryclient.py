from celery import group, chain
from tasks import build_file, index_file, get_count
import ContextClassHarvesters

chunk_size = ContextClassHarvesters.ContextClassHarvester.CHUNK_SIZE

# we iterate through the total number of records
# building and indexing each file in turn
# TODO: add commit + optimize task to end of chord
export = group(chain( build_file.s(i) | index_file.s() ) for i in range(0, get_count.delay().get(), chunk_size ))
export()

# g = [index_file.delay("../entities_out/concepts/concepts_" + str(i) + "_" + str(i + chunk_size) + ".xml") for i in range(0, get_count.delay().get(), chunk_size)]