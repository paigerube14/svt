#!/usr/bin/env python

import time
import subprocess


def invoke(command):
    try:
        output = subprocess.check_output(command, shell=True,
                                         universal_newlines=True)
    except Exception:
        print("Failed to run %s" % (command))
    return output


def get_builds():
    running = invoke("oc get builds -A | grep svt | grep Running -c").strip()
    pending = invoke("oc get builds -A | grep svt | grep Pending -c").strip()

    complete = invoke("oc get builds -A | grep svt | grep Complete -c").strip()
    failed = invoke("oc get builds -A | grep svt | grep Fail -c").strip()

    print("Running " + str(running))
    print("complete " + str(complete))
    print("pending " + str(pending))
    print("failed " + str(failed))

    not_complete = int(running) + int(pending)

    return not_complete

# Main function
def build_status( ):
    print("Starting upgrade check")
    not_complete = get_builds()
    while not_complete > 0:
        not_complete = get_builds()
        time.sleep(30)

build_status()