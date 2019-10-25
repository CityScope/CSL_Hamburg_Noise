#!/bin/sh

docker stop noise_module_instance
docker rm noise_module_instance
docker run --name noise_module_instance -d noise_module
docker logs -f noise_module_instance
