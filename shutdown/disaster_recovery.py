import invoke_command
import time




def no_etcd_revision_nodes():
    return invoke_command.run_cmd("oc get etcd -o=jsonpath='{range .items[0].status.conditions[?(@.type==" + '"NodeInstallerProgressing"' + ")]}{.message}'")


def no_sched_revision_nodes():
    return invoke_command.run_cmd("oc get kubescheduler -o=jsonpath='{range .items[0].status.conditions[?(@.type==" + '"NodeInstallerProgressing"' + ")]}{.message}'")

def no_apiserver_revision_nodes():
    return invoke_command.run_cmd("oc get kubeapiserver -o=jsonpath='{range .items[0].status.conditions[?(@.type==" + '"NodeInstallerProgressing"' + ")]}{.message}'")


etcd_done=False
kube_scheduler_done=False
kube_api_server_done=False

while not etcd_done or not kube_api_server_done or not kube_scheduler_done:

    if not etcd_done:
        etcd = no_etcd_revision_nodes()
        if "revision" not in str(etcd):
            print('setting etcd done')
            etcd_done = True

    if not kube_scheduler_done:
        sched = no_sched_revision_nodes()
        if "revision" not in str(sched):
            print('setting sched done')
            kube_scheduler_done = True


    if not kube_api_server_done:
        api_server = no_apiserver_revision_nodes()
        if "revision" not in str(api_server):
            print('setting api done')
            kube_api_server_done = True

    time.sleep(10)


invoke_command.run_cmd("oc get co")
invoke_command.run_cmd("oc get nodes")
