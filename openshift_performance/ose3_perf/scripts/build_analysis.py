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
import time


def run(cmd, config=""):

    if config:
        cmd = "KUBECONFIG=" + config + " " + cmd
    result = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
    return result


def parse(result, idx):

    status = result['status']['phase']
    namespace = result['metadata']['namespace']
    name = result['metadata']['name']
    duration_string = result['status']['duration']
    global_build_status[idx] = STATUS_STARTED
    if (status.startswith("Failed")) or (status == "Cancelled") or \
            (status.startswith("Error")):
        logger.info("failed cancelled or error")
        if idx in global_build_status.keys():
            #logger.info(idx + " FAILED")
            if global_build_status[idx] < STATUS_NOT_COMPLETE:
                global_build_status[idx] = STATUS_NOT_COMPLETE
                stats_idx = idx[0:idx.rindex('-')]
                global_build_stats[stats_idx]["failed"] += 1
    elif "Complete" == status:
        if idx in global_build_status.keys():
            global_build_status[idx] = STATUS_COMPLETE
            # logger.info(global_build_status[idx])
            do_post_actions_build(result, name, namespace, idx)


def do_post_actions_build(build, build_name, namespace, idx):

    if (global_build_status[idx] >= STATUS_LOGGING) or \
            (global_build_status[idx] < STATUS_COMPLETE):
        return
    global_build_status[idx] = STATUS_LOGGING
    build_time_dur = (build['status']['duration']) / 1e9
    #total duration is in nanoseconds
    for stages in build['status']['stages']:
        if "Push" in stages['name']:
            push_time = stages['durationMilliseconds']
        elif "Fetch" in stages['name']:
            fetch_time = stages['durationMilliseconds']
        elif "Pull" in stages['name']:
            pull_time = stages['durationMilliseconds']
        elif "Build" in stages['name']:
            build_time = stages['durationMilliseconds']

    stats_idx = idx
    # logger.info('stats idx ' + str(stats_idx))
    if (build_time == 0) or (push_time == 0):
        logger.info("Invalid data - not included in summary statistics: " + namespace + ":" + build_name)
        global_build_stats[stats_idx]["invalid"] += 1
        global_build_status[idx] = STATUS_LOGGING_ERROR
    else:
        #logger.info("status logged random push " + str(STATUS_LOGGED))
        global_build_status[idx] = STATUS_LOGGED
        global_build_stats[stats_idx]["num"] += 1
        global_build_stats[stats_idx]["build_time"] += build_time
        global_build_stats[stats_idx]["push_time"] += push_time
        global_build_stats[stats_idx]["fetch_time"] += fetch_time
        global_build_stats[stats_idx]["pull_time"] += pull_time
        global_build_stats[stats_idx]['build_dur'] += build_time_dur
        if build_time > global_build_stats[stats_idx]["max_build"]:
            global_build_stats[stats_idx]["max_build"] = build_time
        if build_time < global_build_stats[stats_idx]["min_build"]:
            global_build_stats[stats_idx]["min_build"] = build_time
        if push_time > global_build_stats[stats_idx]["max_push"]:
            global_build_stats[stats_idx]["max_push"] = push_time
        if push_time < global_build_stats[stats_idx]["min_push"]:
            global_build_stats[stats_idx]["min_push"] = push_time
        if build_time_dur > global_build_stats[stats_idx]["max_build_dur"]:
            global_build_stats[stats_idx]["max_build_dur"] = build_time_dur
        if build_time_dur < global_build_stats[stats_idx]["min_build_dur"]:
            global_build_stats[stats_idx]["min_build_dur"] = build_time_dur


def get_build_configs():
    logger.info('get all build configs')
    all_builds = []
    try:
        output = run("oc get -o json build -A --sort-by '{.metadata.creationTimestamp}' ")
        build_configs = json.loads(output)
        if build_configs:
            for build in build_configs["items"]:
                all_builds.append({"namespace": build["metadata"]["namespace"],
                                "name": build["metadata"]["name"], "build": build})
        #logger.info("all builds " + str(all_builds))
        return all_builds
    except Exception:
        logger.exception("cannot get BCs from the output: " + str(output))
        sys.exit(1)

def get_build_configs_file():
    logger.info('get all build configs file')
    all_builds = []
    try:
        with open("builds.json") as f:
            builds = f.read().replace('\n', '')
            logger.info('builds read' + str(type(builds)))
            build_configs = json.loads(builds)
            logger.info('build load' + str(type(build_configs)))
        if build_configs:
            logger.info('here')
            for build in build_configs["items"]:
                all_builds.append({"namespace": build["metadata"]["namespace"],
                                "name": build["metadata"]["name"], "build": build})
        return all_builds
    except Exception:
        logger.exception("cannot get BCs from the output: ")
        sys.exit(1)

def print_stats(global_build_stats):
    # output stats
    total_all_builds = 0
    total_all_pushes = 0
    total_failed = 0
    total_invalid = 0
    total_builds = 0
    max_all_builds = -1
    min_all_builds = sys.maxint
    max_all_pushes = -1
    min_all_pushes = sys.maxint
    logger.info("all builds " + str(global_build_stats))
    for idx in global_build_stats:
        logger.info('idx ' + str(idx))
        num = global_build_stats[idx]["num"]
        logger.info("\tTotal builds: " +
                    str(global_build_stats[idx]["num"]) +
                    " Failures: " + str(global_build_stats[idx]["failed"]))
        logger.info("\tAvg build time (from duration): " +
                    str((global_build_stats[idx]["build_dur"] / num) / 1000) +
                    " Max build time (from duration): " +
                    str(global_build_stats[idx]["max_build_dur"]) +
                    " Min build time (from duration): " +
                    str(global_build_stats[idx]["min_build_dur"]))
        logger.info("\tAvg build time: " +
                    str(global_build_stats[idx]["build_time"] / num) +
                    " Max build time: " +
                    str(global_build_stats[idx]["max_build"]) +
                    " Min build time: " +
                    str(global_build_stats[idx]["min_build"]))
        logger.info("\tAvg push time: " +
                    str(global_build_stats[idx]["push_time"] / num) +
                    " Max push time: " +
                    str(global_build_stats[idx]["max_push"]) +
                    " Min push time: " +
                    str(global_build_stats[idx]["min_push"]))
        logger.info("\tAvg fetch time: " +
                    str(global_build_stats[idx]["fetch_time"] / num))
        logger.info("\tAvg pull time: " +
                    str(global_build_stats[idx]["pull_time"] / num))
        total_all_builds += global_build_stats[idx]["build_time"]
        if global_build_stats[idx]["max_build"] > max_all_builds:
            max_all_builds = global_build_stats[idx]["max_build"]
        if global_build_stats[idx]["min_build"] < min_all_builds:
            min_all_builds = global_build_stats[idx]["min_build"]

        total_all_pushes += global_build_stats[idx]["push_time"]
        if global_build_stats[idx]["max_push"] > max_all_pushes:
            max_all_pushes = global_build_stats[idx]["max_push"]
        if global_build_stats[idx]["min_push"] < min_all_pushes:
            min_all_pushes = global_build_stats[idx]["min_push"]

        total_builds += global_build_stats[idx]["num"]

        total_failed += global_build_stats[idx]["failed"]
        total_invalid += global_build_stats[idx]["invalid"]

    if total_builds > 0:
        logger.info("Failed builds: " + str(total_failed))
        logger.info("Invalid builds: " + str(total_invalid))
        logger.info("Good builds included in stats: " + str(total_builds))
        logger.info("Average build time, all good builds: " +
                    str(total_all_builds/total_builds))
        logger.info("Minimum build time, all good builds: " +
                    str(min_all_builds))
        logger.info("Maximum build time, all good builds: " +
                    str(max_all_builds))
        logger.info("Average push time, all good builds: " +
                    str(total_all_pushes/total_builds))
        logger.info("Minimum push time, all good builds: " +
                    str(min_all_pushes))
        logger.info("Maximum push time, all good builds: " +
                    str(max_all_pushes))
    else:
        logger.info('total builds <= 0')

def wait_for_running():
    builds_running = run('oc get builds -A | grep Running -c')
    while builds_running > 0:
        time.sleep(2)
        print('builds still running ' + str(builds_running))
        builds_running = run('oc get builds -A | grep Running -c')

def start():
    global global_config
    global global_build_stats
    parser = OptionParser()
    parser.add_option("-b", "--build_num", dest="build_num",
                      help="number of builds to analyze")
    parser.add_option("-n", "--numiter", dest="num", default=1,
                      help="Number of iterations")

    random.seed()

    (options, args) = parser.parse_args()

    global_config["build_num"] = options.build_num
    global_config["num_iterations"] = int(options.num)

    logger.info("Gathering build info...")

    all_builds = get_build_configs()

    logger.info("Build info gathered.")

    build_nums = global_config["build_num"].split(' ')
    all_builds_len = len(all_builds)
    print('length ' + str(all_builds_len))
    # need to go opposite way in array
    last_index = all_builds_len
    for count in reversed(build_nums):
        count = int(count.strip("() ,"))
        print('count2 ' + str(count))
        # count backwards
        for num_iter in range(global_config["num_iterations"]):
            print('num iter ' + str(num_iter) + str(type(num_iter)))

            start_index = last_index - count
            print('start index ' + str(start_index) + " " + str(last_index))
            # # times by iteration count
            # # init statistics
            for build in all_builds[start_index: last_index]:
                idx = str(count) + ":" + str(num_iter)
                if idx not in global_build_stats:
                    global_build_stats[idx] = {"num": 0, "fetch_time": 0, "build_time": 0, "max_build": 0,
                                               "min_build_dur": sys.maxint, "max_build_dur": 0, "build_dur": 0,
                                               "min_build": sys.maxint, "push_time": 0, "pull_time": 0,
                                               "max_push": 0, "min_push": sys.maxint,
                                               "build_time_variance": 0,
                                               "push_time_variance": 0,
                                               "failed": 0, "invalid": 0}
                parse(build['build'], idx)

            last_index = start_index
    print_stats(global_build_stats)

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

def inspect_namespaces():
    i =0
    while i < 2000:
        run('oc adm inspect namespace svt-cakephp-' + str(i))
        i += 1

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
    inspect_namespaces()
    #start()

