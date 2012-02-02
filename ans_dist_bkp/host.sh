#!/bin/sh
ssh -o StrictHostKeyChecking=no -i cloud_key root@rhua "scp -o StrictHostKeyChecking=no -i cloud_key /root/root@rhua_host root@cds1:/root; scp -o StrictHostKeyChecking=no -i cloud_key /root/root@rhua_host root@cds2:/root"

ssh -o StrictHostKeyChecking=no -i cloud_key root@cds1 "scp -o StrictHostKeyChecking=no -i cloud_key /root/root@cds1_host root@rhua:/root; scp -o StrictHostKeyChecking=no -i cloud_key /root/root@cds1_host root@cds2:/root"

ssh -o StrictHostKeyChecking=no -i cloud_key root@cds2 "scp -o StrictHostKeyChecking=no -i cloud_key /root/root@cds2_host root@rhua:/root; scp -o StrictHostKeyChecking=no -i cloud_key /root/root@cds2_host root@cds1:/root"

ssh -o StrictHostKeyChecking=no -i cloud_key root@rhua "cat /root/*_host >> /etc/hosts"

ssh -o StrictHostKeyChecking=no -i cloud_key root@cds1 "cat /root/*_host >> /etc/hosts"

ssh -o StrictHostKeyChecking=no -i cloud_key root@cds2 "cat /root/*_host >> /etc/hosts"
