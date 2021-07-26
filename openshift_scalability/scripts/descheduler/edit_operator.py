import yaml


def print_new_profiles(profiles, fileName):
    # append to file
    with open(fileName, "r") as f:
        yaml_file = yaml.load(f, Loader=yaml.FullLoader)
        print("yaml file " + str(yaml_file))
        yaml_file['spec']['profiles'] = profiles
        print("new yaml file " + str(yaml_file))
    with open(fileName, "w+") as f:
        str_file = yaml.dump(yaml_file)
        print('type ' + str(type(str_file)))
        f.write(str_file)

def print_operator_version(version_url, fileName):
    # append to file
    with open(fileName, "r") as f:
        yaml_file = yaml.load(f, Loader=yaml.FullLoader)
        print("yaml file " + str(yaml_file))
        container_num = 0
        for container in yaml_file['spec']['template']['spec']['containers']:
            if "descheduler-operator" in container['name']:
                env_var_num = 0
                for env_var in container['env']:
                    if env_var['name'] == "IMAGE":
                        print('cotnainer name ' + str(container['name']))
                        print()
                        print("item " + str(yaml_file['spec']['template']['spec']['containers'][container_num]['env'][env_var_num]))
                        yaml_file['spec']['template']['spec']['containers'][container_num]['env'][env_var_num]['value'] = version_url
                    else:
                        env_var_num += 1
            else:
                container_num += 1
        print("new yaml file " + str(yaml_file))
    with open(fileName, "w+") as f:
        str_file = yaml.dump(yaml_file)
        print('type ' + str(type(str_file)))
        f.write(str_file)