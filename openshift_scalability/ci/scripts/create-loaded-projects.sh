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

  #### OCP 4.2: new requirements to run golang cluster-loader from openshift-tests binary:
  ## - Absolute path to config file needed
  ## - .yaml extension is required now in config file name
  ## - full path to the config file  must be under 70 characters total

  MY_CONFIG=$cur_loc/../../config/golang/configCreateLoadedProjects.yaml
  #  echo -e "\nRunning GoLang cluster-loader from openshift-tests binary with config file: ${MY_CONFIG}"
  #  echo -e "\nContents of  config file: ${MY_CONFIG}"
  #cat ${MY_CONFIG}

  VIPERCONFIG=$MY_CONFIG openshift-tests run-test "[sig-scalability][Feature:Performance] Load cluster should populate the cluster [Slow][Serial]"

}

oc version

echo -e "\nOCP cluster info:"
oc version
oc get nodes -o wide
#oc get pods --all-namespaces -o wide

#oc describe node | grep Runtime

#Should already be in openshift_scalability
#cd /root/svt/openshift_scalability
#pwd
#ls -ltr
echo -e "\n\n############## Running cluster-loader ######################"
export KUBECONFIG=${KUBECONFIG-$HOME/.kube/config}
if [ "$TYPE" == "golang" ]; then
  golang_clusterloader

elif [ "$TYPE" == "python" ]; then

  python_clusterloader
else
  echo "$TYPE is not a valid option, available options: golang, python, atomic"

fi

echo -e "\nCurrent bash shell options: $(echo $-)"

echo -e "\nFinished executing GoLang cluster-loader"

oc get pods --all-namespaces -o wide
echo -e "\nTotal number of running pods: $(oc get pods --all-namespaces -o wide | grep -v default | grep -ci running)"

TOTAL_CLUSTERPROJECTS=$(oc get projects | grep -c clusterproject)
echo -e "\nTotal number of clusterproject namespaces created: ${TOTAL_CLUSTERPROJECTS}"

sleep 2

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

oc get projects
