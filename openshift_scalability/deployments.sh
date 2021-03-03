#!/bin/sh

long_sleep() {
  local sleep_time=180
  echo "Sleeping for $sleep_time"
  sleep $sleep_time
}

clean() { echo "Cleaning environment"; oc delete project --wait=true clusterproject0; }

python_clusterloader() {
  MY_CONFIG=deployments.yaml
  ./cluster-loader.py --file=$MY_CONFIG
}

python_clusterloader

long_sleep