# Overview
This directory contains initial scripts for parsing the logs found at http://elasticsearch2.eanadev.org:5601/app/kibana into sessions, and to perform any other data extraction required.

# Dependencies

The various Python scripts all query the underlying ElasticSearch instance at http://elasticsearch2.eanadev.org:9200/ directly. To do so they use the `elasticsearch 5.1.0` and `elasticsearch-dsl 5.0.0` libraries.
