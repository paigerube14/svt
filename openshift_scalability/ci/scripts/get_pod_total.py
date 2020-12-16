import yaml


# Get the project name and number of pods from the yaml we loaded
def get_pod_counts_python(file):
    pod_list = []
    with open(file, "r") as f:
        yaml_file = yaml.load(f, Loader=yaml.FullLoader)
        for proj in yaml_file['projects']:
            for pod in proj['pods']:
                if "total" in pod.keys():
                    pod_list.append([proj['basename'], pod['total']])
    print(pod_list)
    return pod_list

# Get the project name and number of pods from the yaml we loaded
def get_pod_counts_golang(file):

    pod_list=[]
    with open(file, "r") as f:
        yaml_file = yaml.load(f, Loader=yaml.FullLoader)
        for proj in yaml_file['ClusterLoader']['projects']:
            for pod in proj['pods']:
                if "num" in pod.keys():
                    pod_list.append([proj['basename'], pod['num']])
    print(pod_list)
    return pod_list