# bin/bash

# shellcheck disable=SC2164
cd orbisgis_java
java -cp "bin/*:bundle/*:sys-bundle/*" org.h2.tools.Server -pg -trace &
# shellcheck disable=SC2103
cd ..
if [ "$#" -gt 0 ]; then # if command line arguments were given
    python -u grid_listener.py --endpoint $1
else # no command line args -> don't choose endpoint
    python -u grid_listener.py
fi