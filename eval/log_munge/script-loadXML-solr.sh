for file in /home/mmarrero/bin/evalTim/log_munge_master/analysis/via_solr/as_xml/*
do
  curl "http://localhost:8983/solr/logAnalysisCustom/update?commit=true" -H "Content-Type: text/xml" --data-binary @"$file"
done
