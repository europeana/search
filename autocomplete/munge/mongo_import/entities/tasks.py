from celery import Celery, chain, group
from celery.utils.log import get_task_logger
from requests import ConnectionError
from pymongo.errors import ServerSelectionTimeoutError

import ContextClassHarvesters, Indexer

app = Celery('tasks', broker='redis://localhost:6379/', backend='redis://localhost:6379/')
logger = get_task_logger(__name__)

@app.task(name='mongo_import.get_concept_count', bind=True, default_retry_delay=3, max_retries=5)
def get_concept_count(self):
    try:
        concept = ContextClassHarvesters.ConceptHarvester()
        entity_count = concept.get_entity_count()
        return entity_count
    # note that we don't handle all possible exceptions
    # Celery will pass most errors and exceptions onto the logger
    # and set the task status to failure if left unhandled
    # most of the time this is what we want
    except ServerSelectionTimeoutError as ss:
        raise self.retry(exc=ss)

@app.task(name='mongo_import.build_concept_file', bind=True, default_retry_delay=300, max_retries=5)
def build_concept_file(self, start):
    try:
        concept = ContextClassHarvesters.ConceptHarvester()
        entity_list = concept.build_entity_chunk(start)
        status = concept.build_solr_doc(entity_list, start)
        return status
    except ServerSelectionTimeoutError as ss:
        raise self.retry(exc=ss)

@app.task(name='mongo_import.get_agent_count', bind=True, default_retry_delay=3, max_retries=5)
def get_agent_count(self):
    try:
        ag = ContextClassHarvesters.AgentHarvester()
        entity_count = ag.get_entity_count()
        return entity_count
    # note that we don't handle all possible exceptions
    # Celery will pass most errors and exceptions onto the logger
    # and set the task status to failure if left unhandled
    # most of the time this is what we want
    except ServerSelectionTimeoutError as ss:
        raise self.retry(exc=ss)

@app.task(name='mongo_import.build_agent_file', bind=True, default_retry_delay=300, max_retries=5)
def build_agent_file(self, start):
    try:
        ag = ContextClassHarvesters.AgentHarvester()
        entity_list = ag.build_entity_chunk(start)
        status = ag.build_solr_doc(entity_list, start)
        return status
    except ServerSelectionTimeoutError as ss:
        raise self.retry(exc=ss)

@app.task(name='mongo_import.get_place_count', bind=True, default_retry_delay=3, max_retries=5)
def get_place_count(self):
    try:
        ph = ContextClassHarvesters.PlaceHarvester()
        entity_count = ph.get_entity_count()
        return entity_count
    # note that we don't handle all possible exceptions
    # Celery will pass most errors and exceptions onto the logger
    # and set the task status to failure if left unhandled
    # most of the time this is what we want
    except ServerSelectionTimeoutError as ss:
        raise self.retry(exc=ss)

@app.task(name='mongo_import.build_place_file', bind=True, default_retry_delay=300, max_retries=5)
def build_place_file(self, start):
    try:
        pl = ContextClassHarvesters.PlaceHarvester()
        entity_list = pl.build_entity_chunk(start)
        status = pl.build_solr_doc(entity_list, start)
        return status
    except ServerSelectionTimeoutError as ss:
        raise self.retry(exc=ss)

@app.task(name="mongo_import.index_file", bind=True, default_retry_delay=300, max_retries=5)
def index_file(self, writepath):
    solr_indexer = Indexer.Indexer()
    try:
        solr_indexer.index_file(writepath)
    except Indexer.UndefinedFieldException as ufe:
        logger.error(ufe)
    except ConnectionError as ce:
        raise self.retry(exc=ce)
