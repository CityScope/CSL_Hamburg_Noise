# bin/bash

# shellcheck disable=SC2164
cd orbisgis_java
java -cp "bin/*:bundle/*:sys-bundle/*" org.h2.tools.Server -pg -trace &
# shellcheck disable=SC2103
cd ..
python -u grid_listener.py
