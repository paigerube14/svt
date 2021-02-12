#!/bin/bash

proj_yaml="../content/fio/fio-parameters-drain-node.yaml"

pod_array=(5)
#set node1 and 2
worker_nodes=$(oc get nodes | grep worker)

echo "nodes $worker_nodes"
counter=0
for node in $worker_nodes
do
    if [ "$counter" -eq 0 ]; then
      node_1=$node
    fi
    if [ "$counter" -eq 5 ]; then
      node_2=$node
    fi
    if [ "$counter" -eq 10 ]; then
      echo "ERROR: Can only have 2 worker nodes for this test"
      exit 1
    fi
    counter=$((counter + 1))
done
echo "node 1 $node_1 node 2: $node_2"
#Label nodes
oc label node ${node_1} aaa=bbb && oc label node ${node_2} aaa=bbb


#Make node_2 SchedulingDisabled
oc adm cordon ${node_2}

for pods_n in "${pod_array[@]}"
do
  rm loop_$pods_n.log
  python -c "from pod_density.increase_pods import print_new_yaml_temp; print_new_yaml_temp($pods_n,'$proj_yaml')"
  echo "running project count $pods_n"
  python -u ../cluster-loader.py -v -f $proj_yaml
  ../loop_drain_node.sh $node_1 $node_2 $pods_n 25 | tee loop_$pods_n.log
  echo "here: $?"
  oc delete project fiotest0
done

oc adm uncordon ${node_1}
oc adm uncordon ${node_2}