import subprocess
from optparse import OptionParser
import re
import time


def run(command):
    try:
        output = subprocess.Popen(command, shell=True,
                                  universal_newlines=True, stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT)
        (out, err) = output.communicate()
    except Exception as e:
        print("Failed to run %s, error: %s" % (command, e))
    return out


def edit_machine_sets(worker_node_num):

    worker_num = run('oc get nodes | grep worker -c')

    int_worker_num = int(worker_num)
    print ("worker num types " + str((worker_node_num)) + "|" + str((int_worker_num)))
    if int_worker_num != worker_node_num:
        #get machine sets
        machine_sets = run("oc get machinesets -A").strip()
        #skip title
        rand_machine_sets = machine_sets.split('\n')
        # get number of difference
        current_machines = -1
        for machine in rand_machine_sets:
            if current_machines < 0:
                current_machines = 0
                continue
            machine_info = re.split(r'\s{2,}', machine)
            last_machine_set_count = int(machine_info[3])
            current_machines += last_machine_set_count
            machine_set_name = machine_info[1]

        print('machine set info ' + str(machine_set_name))
        wanted_replicas = worker_node_num - current_machines + last_machine_set_count

        #get current numbers
        #add current replcias to wanted num
        print('wanted replicas ' + str(wanted_replicas))
        # get current replicas
        replica_cmd = "oc scale --replicas=" + str(wanted_replicas) + " machineset " + machine_set_name +" -n openshift-machine-api"
        print('replic cmd ' + str(replica_cmd))
        run(replica_cmd)

        counter = 0
        while worker_node_num != int_worker_num:
            worker_num = run('oc get nodes | grep worker -c')
            int_worker_num = int(worker_num)
            time.sleep(30)
            print("waiting 10 seconds for nodes to come up" + str(worker_node_num) + str(int_worker_num))
            counter += 1
            if counter >= 60:
                break


def pods_in_nodes():
    nodes =run("oc get pods -A -o wide | grep svt | awk '{print $8}'")
    node_list = nodes.split('\n')
    node_json= {}
    for node in node_list:
        if node.strip() == "":
            continue
        if node in node_json.keys():
            continue
        count = node_list.count(node)
        node_json[node] = count
        print("There are " + str(count) + " svt pods running on node " + str(node))


def see_if_error_builds(output_file):
    print('here')
    errorbuilds=run('oc get builds --all-namespaces | grep svt | egrep -v "Running|Complete|Creating|Pending"')
    with open(output_file, "a") as f:
        f.write(str(errorbuilds))
    print ("error builds" + str(errorbuilds))
    COUNTER=0
    error_builds_list = errorbuilds.split("\n")
    builds = []

    for val in error_builds_list:
        COUNTER = 0
        error_builds = []
        line = re.split(r'\s{2,}', val)
        for word in line:
            if ((COUNTER % 6 ) == 0 ):
                error_builds.append(word)
            elif ((COUNTER % 6 ) == 1):

                error_builds.append(word)
                builds.append(error_builds)
            else:
                break

            COUNTER += 1

    return builds



def get_error_builds(build_item):
    namespace = build_item[0]
    name = build_item[1]
    #append to file
    with open(name + namespace +".out", "w+") as f:
        f.write("Describing info for " + name + " in namespace "+ namespace + '\n')
        #logs = run("oc describe pod/" + str(name) + " -n " + namespace)
        #f.write("Describe pod " + str(logs) + '\n')
        logs = run("oc describe build " + str(name) + " -n " + namespace)
        f.write("Describe build " + str(logs) + '\n')


def check_error_build(global_output_file):
    builds_list = see_if_error_builds(global_output_file)
    skip_first = True
    for build_item in builds_list:
        if skip_first:
            skip_first = False
        else:
            get_error_builds(build_item)

def see_if_error(output_file):
    print('here')
    errorpods=run('oc get pods --all-namespaces | grep svt | egrep -v "Running|Complete|Creating|Pending"')
    with open(output_file, "a") as f:
        f.write(str(errorpods))
    print ("errorpods" + str(errorpods) + str(type(errorpods)))
    COUNTER=0
    error_pods_list = errorpods.split("\n")
    pods = []

    for val in error_pods_list:
        COUNTER = 0
        error_pods = []
        line = re.split(r'\s{2,}', val)
        for word in line:
            if ((COUNTER % 6 ) == 0 ):
                error_pods.append(word)
            elif ((COUNTER % 6 ) == 1):

                error_pods.append(word)
                pods.append(error_pods)
            else:
                break

            COUNTER += 1

    return pods


def get_error_logs(pod_item, output_file):
    namespace = pod_item[0]
    name = pod_item[1]
    #append to file
    with open(name + namespace +".out", "w+") as f:
        f.write("Debugging info for " + name + " in namespace "+ namespace + '\n')
        #logs = run("oc describe pod/" + str(name) + " -n " + namespace)
        #f.write("Describe pod " + str(logs) + '\n')
        logs = run("oc logs " + str(name) + " -n " + namespace)
        f.write("Logs " + str(logs) + '\n')
        #replicationcontroller=run("oc get replicationcontrollers -n " + namespace)
        #f.write("replication controller output " + str(replicationcontroller) + "\n\n\n")
        #describe_deploy = run("oc describe replicationcontrollers " + replicationcontroller + " -n " + str(namespace))
        #f.write("describe_deploy" + str(describe_deploy))


def check_error(global_output_file):
    pods_list = see_if_error(global_output_file)
    skip_first = True
    for pod_item in pods_list:
        if skip_first:
            skip_first = False
        else:
            get_error_logs(pod_item, global_output_file)

def terminating_pods():

    while True:
        pods = run("oc get pods -A | grep svt | grep Terminating")
        print("pods " + str(pods))
        time.sleep(30)
