#/!/bin/bash
#set -x
################################################
## Auth=vlaad@redhat.com
## Desription: Script for running concurrent
## build tests.
################################################
master=$1
#build_array=(1 5 10 20 30 40 50)
build_array=(1)
#app_array=("cakephp" "eap" "django" "nodejs")
app_array=("cakephp")
registry_url=("registry.centos.org/centos/php-72-centos7")
# this number should be equal to the number of the created projects
readonly PROJECT_NUM=1

function delete_projects()
{
  echo "deleting projects"
  oc delete project -l purpose=test --wait=false
}

function create_projects()
{
  echo "create projects variable $1"
  python ../../../openshift_scalability/cluster-loader.py -f $1
}

function prepare_builds_file()
{
  echo "prepare builds file: $1"
  bc_name=`oc get bc -n  svt-$1-0 --no-headers | awk {'print $1'}`
  local running_build_file
  running_build_file="../content/running-builds.json"
  # generate running-builds.json on the fly
  printf '%s\n' "[" > "${running_build_file}"
  for (( c=0; c<"${PROJECT_NUM}"; c++ ))
  do
    if [[ "$c" == $((PROJECT_NUM - 1)) ]]; then
      printf '%s\n' "{\"namespace\":\"svt-$1-${c}\", \"name\":\"$bc_name\"}" >> "${running_build_file}"
    else
      printf '%s\n' "{\"namespace\":\"svt-$1-${c}\", \"name\":\"$bc_name\"}," >> "${running_build_file}"
    fi
  done
  printf '%s' "]" >> "${running_build_file}"
}

function run_builds()
{
  echo "${build_array[@]}"
  for i in "${build_array[@]}"
  do
    echo "running $i $1 concurrent builds"
    fileName="conc_builds_$1.out"
    python ../../ose3_perf/scripts/build_test.py -z -a -n 2 -r $i -f ../content/running-builds.json >> $fileName 2>&1
    sleep 30
  done
}

function wait_for_build_completion()
{
  echo "oc get pods --all-namespaces | grep svt | grep build | grep Running | wc -l"
  sleep 10
  running=`oc get pods --all-namespaces | grep svt | grep build | wc -l`
  echo "running $running"
  while [ $running -ne 0 ]; do
    sleep 5
    running=`oc get pods --all-namespaces | grep svt | grep build | grep Running | wc -l`
    echo "$running builds are still running"
  done
}

function wait_for_project_termination()
{
  terminating=`oc get projects | grep svt | grep Terminating | wc -l`
  while [ $terminating -ne 0 ]; do
    sleep 5
    terminating=`oc get projects | grep svt | grep Terminating | wc -l`
    echo "$terminating projects are still terminating"
  done
}

function create_custom_image()
{
  export registryurl="registry.centos.org/centos/php-72-centos7"
  echo "oc new-build --binary --strategy=docker --name $1 --build-arg=registryurl=$registryurl"
  #rewrite dockerfile.sample with registryurl
  oc new-build --binary --strategy=docker --name $1 --build-arg=registryurl=$registryurl -e registryurl=$registryurl -n openshift
  oc start-build $1 --from-dir ../content/ -e registryurl=$registryurl -F -n openshift
}

function clean_build_images()
{
  oc delete imagestream.image.openshift.io $1 -n openshift
  oc delete buildconfigs.build.openshift.io $1 -n openshift
}

rm -rf *.out

for app in "${app_array[@]}"
do
  custom_build_image="builder-image-$app"
  clean_build_images $custom_build_image
  #echo "cusotm build image $custom_build_image"
  create_custom_image $custom_build_image
  delete_projects
  wait_for_project_termination
  echo "Starting $app builds" >> conc_builds_$app.out
  create_projects "../content/conc_builds_$app.yaml" $custom_build_image
  wait_for_build_completion
  prepare_builds_file $app
  run_builds $app
  #delete_projects
  #wait_for_project_termination
  echo "Finished $app builds" >> conc_builds_$app.out
  cat conc_builds_$app.out
  #clean_build_images $custom_build_image

done

for proj in "${app_array[@]}"
do
  echo "================ Average times for $proj app =================" >> conc_builds_results.out
  grep "Average build time, all good builds" conc_builds_$proj.out >> conc_builds_results.out
  grep "Average push time, all good builds" conc_builds_$proj.out >> conc_builds_results.out
  grep "Good builds included in stats" conc_builds_$proj.out >> conc_builds_results.out
  echo "==============================================================" >> conc_builds_results.out
done

cat conc_builds_results.out
