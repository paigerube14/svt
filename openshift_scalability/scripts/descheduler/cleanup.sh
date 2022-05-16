
worker_nodes=$(oc get nodes -l node-role.kubernetes.io/worker= -o name)

for worker in ${worker_nodes}; do
  oc label $worker test-zone= --overwrite
  i=$((i+1))
done

source ./common_func.sh
uncordon_all_nodes

oc delete rc --all -n default
oc delete dc --all -n default
oc delete deployment --all -n default
oc delete pvc --all -n default
oc delete pv --all -n default

oc delete pods --all -n default --wait=false
wait_for_pod_deletion "hello"
wait_for_pod_deletion "rcexlc"
wait_for_pod_deletion "rcexpv"

oc delete project -l purpose=test


oc delete configmap cluster -n openshift-kube-descheduler-operator
oc delete deployment cluster -n openshift-kube-descheduler-operator
oc delete service metrics -n openshift-kube-descheduler-operator

oc delete secret kube-descheduler-serving-cert -n openshift-kube-descheduler-operator

oc delete kubedescheduler cluster -n openshift-kube-descheduler-operator

