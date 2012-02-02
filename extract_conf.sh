#!/bin/sh
pushd ~/rhui20/rhui20-iso/Packages > /dev/null
rpm2cpio pulp-0*.rpm | cpio -idmv > /dev/null
rpm2cpio rh-rhui-tools*.rpm | cpio -idmv > /dev/null
rm -f ~/rhui20/pulp.conf ~/rhui20/cds.conf ~/rhui20/rhui-tools.conf  > /dev/null
cp ./etc/pulp/pulp.conf ~/rhui20/
cp ./etc/pulp/cds.conf ~/rhui20/
cp ./etc/rhui/rhui-tools.conf ~/rhui20/
popd > /dev/null
