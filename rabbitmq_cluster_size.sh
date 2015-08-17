#!/bin/bash

output=$( /usr/sbin/rabbitmqctl status 2>&1 )

if [ $? -eq 0 ]
then
    cluster_size=$( /usr/sbin/rabbitmqctl cluster_status | grep running_nodes | sed 's/.*\[\(.*\)\].*/\1/' | sed 's/,/ /' | wc -w )
    echo "status Cluster okay"
    echo "metric cluster_size int $cluster_size"
else
    echo "status Unable to get cluster status"
fi