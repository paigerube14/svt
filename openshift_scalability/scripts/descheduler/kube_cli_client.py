from kubernetes import client, config
from kubernetes.stream import stream
from kubernetes.client.rest import ApiException
import sys
import subprocess

cli = ""

def invoke(command):
    try:
        output = subprocess.check_output(command, shell=True, universal_newlines=True, timeout=60)
    except Exception as e:
        print("Failed to run %s, error: %s" % (command, e))
        sys.exit(1)
    return output


def initialize_clients():
  global cli
  try:
    config.load_kube_config()
    cli = client.CoreV1Api()
  except ApiException as e:
    print("Failed to initialize kubernetes client: %s\n" % e)
    sys.exit(1)

def exec_cmd_in_pod(command, pod_name, namespace, container=None):
    initialize_clients()
    exec_command = ["bash", "-c", command]
    ret = ""
    try:
      if container:
        ret = stream(
          cli.connect_get_namespaced_pod_exec,
          pod_name,
          namespace,
          container=container,
          command=exec_command,
          stderr=True,
          stdin=False,
          stdout=True,
          tty=False,
        )
      else:
        ret = stream(
            cli.connect_get_namespaced_pod_exec,
            pod_name,
            namespace,
            command=exec_command,
            stderr=True,
            stdin=False,
            stdout=True,
            tty=False,
        )
    except Exception as e:
        print("exception "+ str(e))
        return False
    print('ret ' + str(ret))
    return ret