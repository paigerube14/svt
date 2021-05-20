#!/usr/bin/env python2
import re
import subprocess
import json
import time
from datetime import datetime
import random
import sys
from optparse import OptionParser
# pip install futures
from concurrent.futures import ThreadPoolExecutor, wait
# https://github.com/wroberts/pytimeparse
# pip install pytimeparse
from pytimeparse.timeparse import timeparse
import logging


def run(cmd, config=""):

    if config:
        cmd = "KUBECONFIG=" + config + " " + cmd
    try:
        result = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
    except Exception as e:
        #print('exception ' + str(e))
        return 0
    return result


def start():
    i = 0
    while True:
        num_builds = run("oc get builds -A | grep svt -c | xargs").replace("No resources found", "").replace('\n', '')
        running = run("oc get builds -A | grep -E 'Running|Pending|New' -c | xargs").replace("No resources found", "").replace('\n', '')
        complete = run("oc get builds -A | grep Complete -c | xargs").replace("No resources found", "").replace('\n', '')

        logger.info("Build num: " + str(num_builds))
        logger.info("    running: " + str(running))
        logger.info("    complete: " + str(complete))
        time.sleep(5)

        if i % 5 == 0:
            try:
                builds = run("oc get builds -A --sort-by '{.metadata.creationTimestamp}' | grep Running").split('\n')

                if len(builds) > 0:

                    print('longest running build right now: ' + str(builds[0]))
            except:
                #here
                newBuilds = 0
        i += 1

def delete():
    i = 0
    for i in range(20):
        result = run("oc delete project svt-eap-" + str(i) + " --wait=false")
        logger.info('result ' + str(result))


def init_logger(my_logger):
    my_logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler('/tmp/build_test.log')
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(threadName)s '
                                  '- %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    my_logger.addHandler(fh)
    my_logger.addHandler(ch)

global_config = {}
global_build_stats = {}
global_build_status = {}

STATUS_STARTED = 1
STATUS_COMPLETE = 200
STATUS_LOGGING = 210
STATUS_NOT_COMPLETE = 300
STATUS_LOGGED = 301
STATUS_ERROR = 400
STATUS_LOGGING_ERROR = 401

if __name__ == "__main__":
    logger = logging.getLogger('build_test')
    init_logger(logger)
    start()
