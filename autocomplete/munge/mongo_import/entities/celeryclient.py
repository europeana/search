from celery import group, chain
from tasks import build_file, index_file
import ContextClasses

c = ContextClasses.Concept()
max_record = c.get_entity_count()
chunk_size = ContextClasses.ContextualClass.CHUNK_SIZE

export = group(chain( build_file.s(i) | index_file.s() ) for i in range(0, max_record, chunk_size))
export()