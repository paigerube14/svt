#!/bin/sh

long_sleep() {
  local sleep_time=180
  echo "Sleeping for $sleep_time"
  sleep $sleep_time
}


function delete_projects() {
  echo "deleting projects"
  oc delete project -l purpose=test --wait=false
}


python_clusterloader() {
  MY_CONFIG=deployments.yaml
  ./cluster-loader.py --file=$MY_CONFIG
}
SECONDS=0
python_clusterloader
duration=$SECONDS
echo "$(($duration / 60)) minutes and $(($duration % 60)) seconds elapsed."
long_sleep

oc get nodes

oc version

oc cluster-info