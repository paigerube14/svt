#/!/bin/bash
################################################
## Auth=prubenda@redhat.com qili@redhat.com
## Desription: Script for creating objects and validating the descheduler operator 
## moves pods using nodes utilization resources
## Be sure to follow steps in README.md to install descheduler and correct profiles for this test
## Expected profiles:
##    - LifecycleAndUtilization
## Polarion test case: OCP-44291
## https://polarion.engineering.redhat.com/polarion/#/project/OSE/workitem?id=OCP-44291
## Cluster config: 3 master (m5.xlarge or equivalent) with 3 workers
## kube-burner config: perfscale_regerssion_ci/kubeburner-object-templates/descheduler-evict-pvc.yml
## optional PARAMETERS: number of JOB_ITERATION
################################################ 

source ../../common.sh
source node_mem_utilization_env.sh
source ../../../utils/run_workload.sh
source ../../custom_workload_env.sh
source common_func.sh

validate_descheduler_installation "LifecycleAndUtilization"

node=""
worker_nodes=$(oc get nodes -l node-role.kubernetes.io/worker= -o name)
i=0
last_worker=""
first_worker=""
for worker in ${worker_nodes}; do
  if [[ $i -eq 0 ]]; then
    first_worker=$worker
  else
    oc adm cordon $worker
    last_worker=$worker
  fi
  i=$((i + 1))
done



echo "======Use kube-burner to load the cluster with test objects======"
run_workload

uncordon_all_nodes

wait_for_descheduler_to_run

get_descheduler_evicted

pass_or_fail=0
echo $worker_nme
pod_count=$(count_running_pods $NAMESPACE-$JOB_ITERATION $first_worker eap64-mysql)
echo "$pod_count eap64-mysql pods on $first_worker"
if [[ $pod_count -ge 18 ]]; then
  echo "PASS"
  (( ++pass_or_fail ))
else
  echo "FAIL, expected greater than 18 pods on worker node"
fi


echo "======Final test result======"
if [[ ${pass_or_fail} == 1 ]]; then
  echo -e "\nOverall Descheduler - Validate default LifecycleAndUtilization profile Testcase result:  PASS"
  echo "======Clean up test environment======"
  # # delete projects:
  # ######### Clean up: delete projects and wait until all projects and pods are gone
  echo "Deleting test objects"
  delete_project_by_label kube-burner-job

  exit 0
else
  echo -e "\nOverall Descheduler - Validate default LifecycleAndUtilization profile Testcase result:  FAIL"
  echo "Please debug. When debugging is complete, delete all projects using 'oc delete project -l kube-burner-job'"
  exit 1
fi