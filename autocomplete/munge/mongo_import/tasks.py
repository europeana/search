from celery import Celery, chain, group
from celery.exceptions import MaxRetriesExceededError
from celery.utils.log import get_task_logger
from requests import ConnectionError
from pymongo.errors import ServerSelectionTimeoutError

from entities import ContextClassHarvesters

app = Celery('tasks', broker='redis://localhost:6379/', backend='redis://localhost:6379/')
logger = get_task_logger(__name__)

def log_failure(entity_type, chunk_start):
    with open('logs/failed_builds.txt', 'w') as fails:
        msg = entity_type + " build failed with start point " + str(chunk_start) + "\n"
        fails.write(msg)

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
        try:
            raise self.retry(exc=ss)
        except MaxRetriesExceededError:
            log_failure("Concepts", "Count")
            raise self.retry(exc=ss)

@app.task(name='mongo_import.build_concept_file', bind=True, default_retry_delay=300, max_retries=5)
def build_concept_file(self, start):
    try:
        concept = ContextClassHarvesters.ConceptHarvester()
        entity_list = concept.build_entity_chunk(start)
        status = concept.build_solr_doc(entity_list, start)
        return status
    except ServerSelectionTimeoutError as ss:
        try:
            raise self.retry(exc=ss)
        except MaxRetriesExceededError:
            log_failure("Concepts", start)
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
        try:
            raise self.retry(exc=ss)
        except MaxRetriesExceededError:
            log_failure("Agents", "Count")
            raise self.retry(exc=ss)

@app.task(name='mongo_import.build_agent_file', bind=True, default_retry_delay=300, max_retries=5)
def build_agent_file(self, start):
    try:
        ag = ContextClassHarvesters.AgentHarvester()
        entity_list = ag.build_entity_chunk(start)
        status = ag.build_solr_doc(entity_list, start)
        return status
    except ServerSelectionTimeoutError as ss:
        try:
            raise self.retry(exc=ss)
        except MaxRetriesExceededError:
            log_failure("Agents", start)
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
        try:
            raise self.retry(exc=ss)
        except MaxRetriesExceededError:
            log_failure("Places", "Count")
            raise self.retry(exc=ss)

@app.task(name='mongo_import.build_place_file', bind=True, default_retry_delay=300, max_retries=5)
def build_place_file(self, start):
    try:
        pl = ContextClassHarvesters.PlaceHarvester()
        entity_list = pl.build_entity_chunk(start)
        status = pl.build_solr_doc(entity_list, start)
        return status
    except ServerSelectionTimeoutError as ss:
        try:
            raise self.retry(exc=ss)
        except:
            log_failure("Places", start)
            raise self.retry(exc=ss)
