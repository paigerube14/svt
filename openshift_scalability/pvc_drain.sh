#/!/bin/bash

pvc=25
results_file=pvc_drain.out
loader_file=./content/fio/fio-parameters-drain-node.yaml
cloud_provider=aws

function create_projects() {
  echo "create projects variable $loader_file"
  python cluster-loader.py -f $loader_file -v
}

function rewrite_yaml() {
  python -c "from scripts.pod_density import increase_pods; increase_pods.print_new_yaml_temp($1,'$loader_file')"
}


function delete_projects()
{
  echo "deleting pvc"
  oc delete pvc --all -n fiotest0
  oc delete pods --all -n fiotest0
}

function wait_for_project_termination()
{
  terminating=`oc get pv | grep pvcproject0 | wc -l`
  while [ ${terminating} -ne 0 ]; do
  sleep 5
  terminating=`oc get pv | grep pvcproject0 | wc -l`
  echo "$terminating pv are still there"
  done
}

function wait_for_running() {

  not_running=`oc get pods -A -o wide | grep fiotest | grep -E "Creating|Pending" | grep $1 | wc -l | xargs`
  while [ ${not_running} -ne $pvc ]; do
  sleep 5
  terminating=`oc get pv -A -o wide | grep fiotest | grep -E "Creating|Pending" | grep $1 | wc -l | xargs`
  echo "$not_running pvc pods are still not running on node $1"
  done
}


rm -irf $results_file

declare -a node_array

compute_nodes=$(oc get nodes -l 'node-role.kubernetes.io/worker=' | awk '{print $1}' | grep -v NAME | xargs)
counter=0
for n in ${compute_nodes}; do
  node_array[${counter}]=${n}
  echo "counter $counter $n"
  counter=$((counter+1))
done
echo ${node_array[1]}
#
#echo "Cordon node ${node_array[0]}"
#oc adm cordon ${node_array[0]}
##echo "Pvc num: $pvc " >> $results_file
#rewrite_yaml $pvc
#create_projects
echo "Wait for all pods to be running on node ${node_array[1]}"
wait_for_running ${node_array[1]}
#echo "Uncordon node ${node_array[0]}"
#oc adm uncordon ${node_array[0]}
#start_time=`date +%s`oo
#echo "Drain node ${node_array[1]}"
#oc adm drain ${node_array[1]}
#wait_for_running ${node_array[0]}
#total_time=`echo $stop_time - $start_time | bc`
#echo -e "\t Iteration $i Drain Time - $total_time" >> $results_file
#start_time=`date +%s`
#delete_projects
#wait_for_project_termination
#stop_time=`date +%s`
#total_time=`echo $stop_time - $start_time | bc`
#echo -e "\t Iteration $i Deletion Time - $total_time" >> $results_file
#cat $results_file