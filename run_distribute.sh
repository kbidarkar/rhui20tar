#!/bin/bash 
#Distribute the rpms and install
chmod 600 cloud_key
rhui-installer /root/rhui20/answers_file
pushd /tmp/rhui > /dev/null
yum localinstall rh-rhua* -y --nogpgcheck
scp -o StrictHostKeyChecking=no -i cloud_key rh-cds1*.rpm root@cds1:/root ; ssh -o StrictHostKeyChecking=no -i cloud_key root@cds1 "yum localinstall rh-cds1* -y --nogpgcheck"
scp -o StrictHostKeyChecking=no -i cloud_key rh-cds2*.rpm root@cds2:/root ; ssh -o StrictHostKeyChecking=no  -i cloud_key root@cds2 "yum localinstall rh-cds2* -y --nogpgcheck"
popd > /dev/null
