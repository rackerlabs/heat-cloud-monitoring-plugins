#!/bin/bash

HOME='/root'
mysql_output=$( mysql --defaults-file=/root/.my.cnf -NB -e 'show status like "wsrep_flow_control_paused"' 2>&1 )

if [ $? -eq 0 ]
then
    wsrep_fcp=$( echo $mysql_output | awk '{ print $2 }' )
    wsrep_ready=$( mysql --defaults-file=/root/.my.cnf -NB -e 'show status like "wsrep_ready"' 2>&1 | awk '{ print $2 }' )
    wsrep_connected=$( mysql --defaults-file=/root/.my.cnf -NB -e 'show status like "wsrep_connected"' 2>&1 | awk '{ print $2 }' )
    wsrep_local_state=$( mysql --defaults-file=/root/.my.cnf -NB -e 'show status like "wsrep_local_state_comment"' 2>&1 | awk '{ print $2 }' )
    wsrep_cluster_size=$( mysql --defaults-file=/root/.my.cnf -NB -e 'show status like "wsrep_cluster_size"' 2>&1 | awk '{ print $2 }' )
    wsrep_status=$( mysql --defaults-file=/root/.my.cnf -NB -e 'show status like "wsrep_cluster_status"' | awk '{ print $2 }' )

    if [ "$wsrep_ready" != "ON" ]
    then
        if [ "$wsrep_connected" != "ON" ]
        then
            echo "status wsrep_connected OFF"
            exit 1
        else
            echo "status wsrep not ready: ${wsrep_local_state}"
            exit 1
        fi
    else
        echo "status wsrep_ready ON"
        echo "metric wsrep_cluster_size int $wsrep_cluster_size"
        echo "metric wsrep_flow_control_paused float $wsrep_fcp"
        echo "metric wsrep_status string $wsrep_status"
    fi
else
    echo "status MySQL error: $mysql_output"
        exit 1
fi
