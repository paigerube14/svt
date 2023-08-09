# WORKLOAD_TEMPLATE for custom workload of kube-burner
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export WORKLOAD_TEMPLATE=${WORKLOAD_TEMPLATE:-"${DIR}/../../../kubeburner-object-templates/descheduler-node-utilization.yml"}
# ENVs to overwrite the kube-burner configuration file
export NAME=${NAME:-"node-util-desched"}
export NAMESPACE=${NAMESPACE:-"node-util-desched"}
export WAIT_FOR=["PersistentVolumeClaim","ReplicationController"]
export JOB_ITERATION=${JOB_ITERATION:=1}