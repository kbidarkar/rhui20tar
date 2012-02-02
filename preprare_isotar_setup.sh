#!/bin/sh
echo -e "Please enter your userid"
read userid
echo -e "Please enter the iso_location"
read iso_loc
[ ! -d /home/$userid/rhui20 ] && mkdir /home/$userid/rhui20
tar -xvf rhui20_installation.tar
cp -R ./rhui20tar/ans_dist_bkp ./rhui20tar/gen_certs.tar ./rhui20tar/extract_conf.sh ./rhui20tar/hostname.sh ./rhui20tar/install_rhui_iso.py ./rhui20tar/reset.sh ./rhui20tar/rhui_lib.py ./rhui20tar/run_distribute.sh /home/$userid/rhui20

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



chown -R  $userid.$userid /home/$userid/rhui20/rhui20-iso
chmod -R  755 /home/$userid/rhui20/rhui20-iso
chown $userid.$userid /home/$userid/rhui20/rhui20-iso.tar
