import re
import sys
from datetime import datetime
import time

def percent_difference( new, old):
    r1 = (new - old)
    response = ((r1) / old)
    r2 = response * 100
    return r2


def get_time_from_str(oc_str):
    oc_time = datetime.strptime(oc_str, "%Mm%S.%fs")
    total_seconds = (oc_time.microsecond / 1000000.0) + (oc_time.second) + (oc_time.minute * 60)
    return total_seconds

def compare_oc_times(json_1, json_2):
    for v1 in json_1:
        for v2 in json_2:

            real_compare = percent_difference(get_time_from_str(v1[0]), get_time_from_str(v2[0]))
            user_compare = percent_difference(get_time_from_str(v1[1]), get_time_from_str(v2[1]))
            sys_compare = percent_difference(get_time_from_str(v1[2]), get_time_from_str(v2[2]))
            print('\tReal time difference ' + str(real_compare) + "%")
            print('\tUser time difference: ' + str(user_compare) + "%")
            print('\tSys time difference: ' + str(sys_compare) + "%")

def read_file(file):
    all_file = []

    oc_split = re.split("\n", file)
    i = 0
    new_time = []
    for line in oc_split:
        # first is name
        if line == "" or "\n" == line:
            continue
        elif i % 4 == 0:
            if i / 4 == 1:
                all_file.append({'create': new_time})
            elif i / 4 == 2:
                all_file.append({'get': new_time})

            elif i /4 == 3:
                all_file.append({'scale': new_time})

            new_time = []
        else:
            line_split = re.split('\t', line)[-1]
            line_split = re.split(r"[ ]+", line_split)[-1]
            new_time.append(line_split)
        i += 1
    all_file.append({'delete': new_time})
    print('all file ' + str(all_file))
    return all_file

if len(sys.argv) > 3 or len(sys.argv) <= 2:
    print("Need 2 build files to compare")
    sys.exit(1)

#get command line parameters
file_1 = sys.argv[1]
file_2 = sys.argv[2]

with open(file_1, "r") as f1:
    f1_content = f1.read()

f1_list = read_file(f1_content)

with open(file_2, "r") as f2:
    f2_content = f2.read()

f2_list = read_file(f2_content)


f2_list
for item_1 in f1_list:
    for item_2 in f2_list:
        if item_1.keys() == item_2.keys():
            print(str(list(item_1.keys())[0]))
            compare_oc_times(item_1.values(), item_2.values())
            break







