#!/bin/bash

queue_name=$1

vhost=$( /usr/sbin/rabbitmqctl list_vhosts | grep heat | tail -n1 )
queue_count=$( /usr/sbin/rabbitmqctl list_queues -p ${vhost} | egrep "^${queue_name}\s+" | cut -f2 )

if [ $? -eq 0 ]
then
  if [ ! -z $queue_count ]
  then
    echo "status RabbitMQ responding"
    echo "metric ${queue_name}_size int ${queue_count}"
    exit 0
  else
    echo "status ${queue_name} size unavailable"
    exit 1
  fi
else
  echo "status Unable to get queue size"
  exit 1
fi
