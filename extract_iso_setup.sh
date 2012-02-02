#!/bin/sh
echo -e "Please enter your userid"
read userid
echo -e "Please enter the iso_location"
read iso_loc

#Setup rhui20 directory
if [ ! -d /home/$userid/rhui20 ] ; then
    mkdir /home/$userid/rhui20
    tar -xvf rhui202_installation.tar
    cp -R ./rhui20tar/ans_dist_bkp ./rhui20tar/gen_certs.tar ./rhui20tar/extract_conf.sh ./rhui20tar/hostname.sh ./rhui20tar/install_rhui_iso.py ./rhui20tar/reset.sh ./rhui20tar/rhui_lib.py ./rhui20tar/run_distribute.sh ./rhui20tar/qpid_cert_gen.sh ./rhui20tar/amazon_ec2_lib.py ./rhui20tar/amazon_ec2.py ./rhui20tar/ans_dist_bkp/host.sh ./rhui20tar/ans_dist_bkp/answers_file /home/$userid/rhui20
else
    echo -e "\nrhui20 Directory already exists, skipping."
fi

#Mount rhui-iso and create rhui-iso.tar excluding SRPMS.
umount /mnt/rhui-iso
pushd /home/$userid/rhui20 > /dev/null
mv /home/$userid/rhui20/rhui20-iso.tar /home/$userid/rhui20/rhui20-iso-old/rhui20-iso-old-`date | awk -F" " '{print $4}'`.tar
rm -rf ./rhui20-iso
popd > /dev/null
mount -t iso9660 -o loop $iso_loc /mnt/rhui-iso/
pushd /mnt/rhui-iso > /dev/null
tar --exclude=./SRPMS -cvf /home/$userid/rhui20/rhui20-iso.tar ./*
popd > /dev/null

pushd /home/$userid/rhui20 > /dev/null
mkdir rhui20-iso ; mv rhui20-iso.tar ./rhui20-iso
popd > /dev/null

pushd /home/$userid/rhui20/rhui20-iso > /dev/null
tar -xvf rhui20-iso.tar ; rm -f rhui20-iso.tar
popd > /dev/null

pushd /home/$userid/rhui20 > /dev/null
tar -cvf rhui20-iso.tar ./rhui20-iso
popd > /dev/null

#permission restore to that of the user.
chown -R  $userid.$userid /home/$userid/rhui20
chmod -R  755 /home/$userid/rhui20/rhui20-iso
