#!/bin/sh

if [ "$#" -gt 0 ]; then # if command line arguments were given
    docker stop noise_module_instance_$1
    docker rm noise_module_instance_$1
    docker run --name noise_module_instance_$1 -d noise_module $1
    # docker logs -f noise_module_instance_$1  ## do not force logs when multiple instances start

else # no command line args -> don't choose endpoint
    docker stop noise_module_instance
    docker rm noise_module_instance
    docker run --name noise_module_instance -d noise_module
    docker logs -f noise_module_instance
fi
