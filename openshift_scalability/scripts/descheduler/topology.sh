node1=""
node2=""
node3=""

source ./common_func.sh

worker_nodes=$(oc get nodes -l node-role.kubernetes.io/worker= -o name)
i=0
for worker in ${worker_nodes}; do
  echo "worker nodes ----  $worker"
  if [[ $i -eq 0 ]]; then
    node1=$worker
  else
    oc adm cordon $worker
  fi
  i=$((i+1))
done

# use cluster loader to load 200+ pods per node

wait_for_pod_creation pod_name

oc get pods -o wide

uncordon_all_nodes

#wait 5 minutes

# get tail of logs from cluster-* pod in -n openshift-kube-descheduler-operator



