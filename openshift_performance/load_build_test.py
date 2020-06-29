import subprocess
import logging


def run(cmd, config=""):

    if config:
        cmd = "KUBECONFIG=" + config + " " + cmd
    result = subprocess.Popen(cmd, stderr=subprocess.STDOUT, shell=True)

    (out,err)=result.communicate()
    print("out " + str(out))
    return out


def create_auto_namespace(counter, app_name):
    for i in range(counter):
        namespace = "auto-proj-" + str(i)
        create_new_app(app_name, namespace)


def does_namespace_exist(namespace):

    namespace_exist = run("oc get projects | grep " + namespace)
    logging.info("name space exist? " + str(namespace_exist))
    if not namespace_exist:
        run("oc new-project " + namespace)


def create_new_app(name, namespace):
    does_namespace_exist(namespace)
    nameapp_exist = run("oc new-app " + name + " -n " + namespace)
    logging.info("name app? " + str(nameapp_exist))


i = 0
app = "cakephp-mysql-example"
while i < 75:
    namespace = "auto-proj-" + str(i)
    create_new_app(app, namespace)
    i += 1