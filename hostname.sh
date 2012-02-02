#!/bin/bash
ip=`hostname -i | awk -F" " '{ print $NF }'`
host_full=`hostname -f`
host_nam=`hostname`
echo "$ip" "             " "$host_full" "             " "$host_nam" > /root/`hostname -f`_host

hostname "$host_full"
