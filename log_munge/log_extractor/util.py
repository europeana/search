import datetime
from collections import namedtuple

UnknownInteraction = namedtuple('UnknownInteraction', 'timestamp session_id message')
SearchInteraction = namedtuple('SearchInteraction', 'timestamp session_id search_term constraints result_count')
RankedRetrieveRecordInteraction = namedtuple('RankedRetrieveRecordInteraction', 'timestamp session_id search_term constraints uri rank result_count')

def create_date_object(iso_8601_date):
    # TODO: expand possible precisions - right now this automatically
    # runs midnight-to-midnight
    aug_iso_8601_date = str(iso_8601_date) +  "T00:00:00.005Z"
    date_as_obj = datetime.datetime.strptime(aug_iso_8601_date, "%Y-%m-%dT%H:%M:%S.%fZ")
    return date_as_obj

def convert_iso_8601_date_to_int(iso_8601_date):
    # TODO: add error-checking
    # TODO: use regex replace for all ˆ\d chars
    as_int = iso_8601_date.replace("-", "")
    return int(as_int)
