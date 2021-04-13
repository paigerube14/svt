#!/bin/sh
echo "build sh"
# Note that in this case the build inputs are part of the custom builder image, but normally this
# would be retrieved from an external source.
cd /tmp/input
# OUTPUT_REGISTRY and OUTPUT_IMAGE are env variables provided by the custom
# build framework
TAG="${OUTPUT_REGISTRY}/${OUTPUT_IMAGE}"

buildah info

# performs the build of the new image defined by Dockerfile.sample
buildah bud --isolation chroot -t ${TAG} .

# buildah requires a slight modification to the push secret provided by the service
# account in order to use it for pushing the image
cp /var/run/secrets/openshift.io/push/.dockercfg /tmp
(echo "{ \"auths\": " ; cat /var/run/secrets/openshift.io/push/.dockercfg ; echo "}") > /tmp/.dockercfg

echo "tag $TAG"
# push the new image to the target for the build
echo "Pushing"
buildah push --tls-verify=false --authfile /tmp/.dockercfg ${TAG}
echo "Successfully pushed"