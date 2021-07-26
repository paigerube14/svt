#https://polarion.engineering.redhat.com/polarion/#/project/OSE/workitem?id=OCP-36587

last_worker=""
for worker in ${worker_nodes}; do
  echo "worker nodes ----  $worker"
  if [[ $i -eq 0 ]]; then
    echo "worker nodes ---- 2 $worker"
    oc debug $worker -- chroot /host mkdir /mnt/data
  else
    oc adm cordon $worker
    last_worker=$worker
  fi
  echo "i $i"
  i=$((i+1))
done

#Verify that pods created from step5 to step8 are not evicted

oc create -f content/pv_local_storage.yaml

oc get pv

# shouldn't get evicted
oc create -f content/pvc.yaml

oc get pv task-pv-volume

oc create -f content/rc.yaml

oc create -f content/dameon_set.yaml

# shouldn't get evicted
oc create -f content/critical-pod.yaml


