from celery import Celery, chain, group
import ContextClasses, Indexer

app = Celery('tasks', broker='redis://localhost:6379/', backend='redis://localhost:6379/')

@app.task(name='mongo_import.build_file')
def build_file(start):
    concept = ContextClasses.Concept()
    entity_list = concept.build_entity_chunk(start)
    status = concept.build_solr_doc(entity_list, start)
    return status

@app.task(name="mongo_import.index_file")
def index_file(writepath):
    print(writepath + "!")
    solr_indexer = Indexer.Indexer()
    solr_indexer.index_file(writepath)