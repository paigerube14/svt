ARG registryurl
FROM $registryurl
#registry.centos.org/centos/php-72-centos7

USER root
RUN yum install -y buildah

ENV registryurl=$registryurl

# Add application sources to a directory that the assemble script expects them
# and set permissions so that the container runs without root access
# In this example, `/tmp/build` contains the inputs that build when this
# custom builder image is run. Normally the custom builder image fetches
# this content from some location at build time, by using git clone as an example.
ADD dockerfile.sample /tmp/input/Dockerfile
ADD build.sh /usr/bin
RUN chmod a+x /usr/bin/build.sh
# /usr/bin/build.sh contains the actual custom build logic that will be run when
# this custom builder image is run.
ENTRYPOINT ["/usr/bin/build.sh"]