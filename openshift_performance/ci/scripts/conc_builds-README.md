## Concurrent builds README

### Purpose
The conc_builds.sh scripts is a flexible tool for driving builds in OpenShift.  This test is intended to reocrd the times of concurrent builds of a specific application and the time it takes to push the image to a registry.

It combines many different tools including cluster-loader and build_test 

### Install python packages

```
$ pip install pytimeparse logging pyyaml rbd rados

## conc_builds README

### Purpose 
The conc_builds.sh scripts is a tool to test the time of build and push times of concurrent builds in OpenShift. 


### Use Python2

The following command should return python 2
```
$ python --version 
```

If not, consider using a python 2 virtual environment.
Information can be found [here](https://docs.python-guide.org/dev/virtualenvs/) on how to install and set the virtual environment 

Activate the virutal environemnt using 
```
$ source <virtualenv_name>/bin/activate
```

Now the same command should return 2.* if done correctly 
```
$ python --version 
```

### Install Requirements 

Install [pytimeparse](https://github.com/wroberts/pytimeparse) module


```
$ pip install -r ../../../openshift_scalability/cluster_loader_requirements.txt
```

### Setup

**Projects and applicatons:**  It is recommended that [cluster-loader](https://github.com/openshift/svt/blob/master/openshift_scalability/README.md) be used to create projects, deployments, build configurations, etc.   **build_test** is a complimentary tool that can run the builds created by **cluster_loader**.

An example cluster-loader config that works with build_test.py is [master-vert.yaml](https://github.com/openshift/svt/blob/master/openshift_scalability/config/master-vert-pv.yaml)

This will create namespaces as below.  These projects will be specified in the build_test json config.
svt-<app_name>-<number>

```
# oc get ns
NAME                 STATUS    AGE
svt-<app_name>-0     Active    2h
svt-<app_name>-1     Active    2h
svt-<app_name>-2     Active    2h
...
```

### Usage 

```./conc_builds.sh```


### Common Errors
If no times are outputed at the end of the concurrent build test, take a look at each of the conc_builds_<app_name>.out files

If no build status information, verify that you are using python 2 
```
2021-01-07 14:27:42,361 - build_test - MainThread - INFO - Gathering build info...
2021-01-07 14:27:42,361 - build_test - MainThread - INFO - Build info gathered.
2021-01-07 14:27:42,363 - build_test - MainThread - INFO - 2021-01-07 14:27:42: iteration: 1
2021-01-07 14:27:42,364 - build_test - MainThread - INFO - All threads started, starting builds
2021-01-07 14:27:42,690 - build_test - MainThread - INFO - check_build_status ...
2021-01-07 14:28:02,711 - build_test - MainThread - INFO - 2021-01-07 14:28:02: iteration: 2
2021-01-07 14:28:02,712 - build_test - MainThread - INFO - All threads started, starting builds
2021-01-07 14:28:03,064 - build_test - MainThread - INFO - check_build_status ..
```

If error includes not being able to find latest tagged image (like below)
```2021-01-07 17:56:55,548 - build_test - ThreadPoolExecutor-0_0 - ERROR - Command failed:  tproject=svt-cakephp-67,cmd=oc start-build -n svt-cakephp-67 cakephp-mysql-example, retcode=1, output=The ImageStreamTag "php:7.2" is invalid: from: Error resolving ImageStreamTag php:7.2 in namespace openshift: unable to find latest tagged image
2021-01-07 17:56:55,548 - build_test - MainThread - INFO - check_build_status ...
2021-01-07 17:57:15,560 - build_test - MainThread - INFO - 2021-01-07 17:57:15: iteration: 2
2021-01-07 17:57:15,560 - build_test - MainThread - INFO - All threads started, starting builds
2021-01-07 17:57:15,847 - build_test - ThreadPoolExecutor-2_0 - ERROR - Command failed:  tproject=svt-cakephp-13,cmd=oc start-build -n svt-cakephp-13 cakephp-mysql-example, retcode=1, output=The ImageStreamTag "php:7.2" is invalid: from: Error resolving ImageStreamTag php:7.2 in namespace openshift: unable to find latest tagged image
```

You'll need to edit the version of the imagestream to latest or a specific version in svt/openshift_scalability/content/quickstarts/<app_name>/<app_name>_build.json 

You can find the latest version by the following: 
```oc get imagestreamtag -A | grep <image_stream> ```

If you want to change the number of projects you have to edit the number of projects in conc_builds.sh as well as the num field at the top of the [yaml files](https://github.com/openshift/svt/tree/master/openshift_performance/ci/content) specific for the application.  By default conc_builds and the content yaml files create 75 projects




### Usage

```./conc_builds.sh ```


### Debugging steps

```oc get builds -A``` (--all-namespaces if before 4.0)

```oc describe build/<buildName> -n <namespace>```
 
```oc get pods -A ```

```oc describe pod/<podName> -n <namespace> ```
  
```oc logs <podName> -n <namespace> | grep error```




### Solutions to issues


https://access.redhat.com/solutions/3467561

https://docs.openshift.com/container-platform/3.10/install_config/registry/registry_known_issues.html
