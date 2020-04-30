for file in /media/mmarrero/data/SearchEvaluation/April2020/28Nov19_1Feb2020/as_xml/*
do
  curl "http://localhost:8983/solr/logAnalysisCustom/update?commit=true" -H "Content-Type: text/xml" --data-binary @"$file"
done
