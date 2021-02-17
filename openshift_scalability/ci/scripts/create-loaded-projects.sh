#!/bin/bash 

if [ "$#" -ne 1 ]; then
  echo "syntax: $0 <TYPE>"
  echo "<TYPE> should be either golang or python"
  exit 1
fi

TYPE=$1

function python_clusterloader() {
  MY_CONFIG=../../config/configCreateLoadedProjects.yaml
  python --version
  python ../../cluster-loader.py -f $MY_CONFIG
}

function golang_clusterloader() {

  # start GoLang cluster-loader
  export KUBECONFIG=${KUBECONFIG-$HOME/.kube/config}
  cur_loc=$(pwd)

  MY_CONFIG=$cur_loc/../../config/golang/configCreateLoadedProjects.yaml

  VIPERCONFIG=$MY_CONFIG openshift-tests run-test "[sig-scalability][Feature:Performance] Load cluster should populate the cluster [Slow][Serial]"

}

function wait_for_project_termination() {
  COUNTER=0
  terminating=$(oc get projects | grep $1 | wc -l)
  while [ $terminating -ne 0 ]; do
    sleep 15
    terminating=$(oc get projects | grep $1 | wc -l)
    echo "$terminating projects are still there"
    COUNTER=$((COUNTER + 1))
    if [ $COUNTER -ge 20 ]; then
      echo "$terminating projects are still there after 5 minutes"
      exit 1
    fi
  done
}

echo -e "\nOCP cluster info:"
oc version
oc get nodes -o wide

oc describe node | grep Runtime

echo -e "\n\n############## Running cluster-loader ######################"
export KUBECONFIG=${KUBECONFIG-$HOME/.kube/config}
if [ "$TYPE" == "golang" ]; then
  golang_clusterloader

elif [ "$TYPE" == "python" ]; then

  python_clusterloader
else
  echo "$TYPE is not a valid option, available options: golang, python, atomic"

fi

echo -e "\nFinished executing GoLang cluster-loader"

pods=$(oc get pods --all-namespaces -o wide | grep clusterproject | grep -ci running)
echo -e "\nTotal number of running pods: $pods"

TOTAL_CLUSTERPROJECTS=$(oc get projects | grep -c clusterproject)
echo -e "\nTotal number of clusterproject namespaces created: ${TOTAL_CLUSTERPROJECTS}"

sleep 20

for (( c=0; c<${TOTAL_CLUSTERPROJECTS}; c++ ))
do
  oc get all -n clusterproject${c}
done

echo -e "\nSleeping for 10 mins"
sleep 600

echo -e "\nDeleting the ${TOTAL_CLUSTERPROJECTS} projects we just created"
for (( c=0; c<${TOTAL_CLUSTERPROJECTS}; c++ ))
do
  oc delete project clusterproject${c}
done

wait_for_project_termination clusterproject
