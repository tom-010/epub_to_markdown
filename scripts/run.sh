#!/bin/bash

#basename "$FILE"
full_name=$1
base_name=$(basename "${full_name}")
dir_name=$(dirname "${full_name}")
dir_name=$(realpath "$dir_name")

mkdir out 2> /dev/null || true 

CONTAINER="tom010/epub_to_markdown"

docker run \
    -v $dir_name:/input \
    -v $(pwd)/out:/out \
    $CONTAINER \
    --out="/out" \
    --epub="/input/$base_name"


# fix permissions
# Give evey folder the permissions: dr-xr-xr-x   -> x allows you to iterate on the folder
# Give every file the permissions:  -rw-r--r--   -> no x, which would make files executable. Writable only by the user, everyone can read
# The idea is to use the docker-conatiner, whose root user can maniuplate the permissions without sudo
# otherwise, we would need to use sudo
USER_ID="$(id -u):$(id -g)" # Fake the user within the docker container
docker run \
    -v $(pwd)/out:/out \
    --entrypoint '/bin/bash' \
    $CONTAINER \
    -c "chown -R $USER_ID /out && find /out -type d -exec chmod 755 {} \; && find /out -type f -exec chmod 644 {} \;"
