# Graphite-Threshold-Alert-System
A customisable system that sits between graphite client and graphite backend server monitoring thresholds and sending alerts to relevant people

Dependencies
--------------
Python version 2.7 > greater
Graphite/Grafana available from URL, http://graphite.wikidot.com/

Design
---------
GTA System would receive input the same way you would push requests to graphite backend, an example is provide below;

cat /var/log/applications/some_info.log | grep "`date +%Y' '%b' '%d" "%H:%M --date '-5 min'`" |  grep -ic "some_unique_value"| xargs -I {} echo ` hostname`-Service-Failure-Rate {} `date +%s` |nc localhost 3001

Principle: The ` hostname`-Service-Failure-Rate, should be configured in the conf/props.ini on the value, WATCH_SERVICES. An alert will be sent based on the conditions provided. If not configured, then GTA will just do normal routing

Tests
----------
Run the server using the init_script.sh, init_script.sh start. Server listens on port 10000

Send data using netcat, echo "KE-B2C-SAF-Service-Failure-Rate-37-`date +%s`" |nc localhost 10000

Project Status
---------------
Dev is Open and On-going
