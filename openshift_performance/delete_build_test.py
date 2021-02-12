import subprocess
import logging
import time

def run(cmd, config=""):

    if config:
        cmd = "KUBECONFIG=" + config + " " + cmd
    result = subprocess.Popen(cmd, stderr=subprocess.STDOUT, shell=True)



def wait_for_project_termination():
  terminating=run("oc get projects | grep Terminating | wc -l")
  while terminating > 0:
      time.sleep(5)
      terminating=run("oc get projects | grep Terminating | wc -l")
      print( "$terminating projects are still terminating")


def delete_auto_namespace(name, counter, startCounter=0):
    i = startCounter
    while i <= counter:
        namespace = name + str(i)
        run("oc delete project/"+namespace)
        i += 1

delete_auto_namespace("auto-proj-", 75)
delete_auto_namespace("svt-eap-", 75)
delete_auto_namespace("svt-cakephp-", 75)
delete_auto_namespace("svt-rails-", 75)
delete_auto_namespace("svt-nodejs-", 75)
wait_for_project_termination()
