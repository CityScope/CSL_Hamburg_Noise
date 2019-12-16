#!/bin/sh

docker stop noise_module_instance
docker rm noise_module_instance
if [ "$#" -gt 0 ]; then # if command line arguments were given
    docker run --name noise_module_instance -d noise_module $1
else # no command line args -> don't choose endpoint
    docker run --name noise_module_instance -d noise_module
fi
docker logs -f noise_module_instance
