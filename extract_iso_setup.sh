#!/bin/sh
echo -e "Please enter your userid"
read userid
echo -e "Please enter the iso_location"
read iso_loc
echo -e "Please enter the full_path location of the rhui20tar repo"
read repo1

tar -cvf /root/rhui202_installation.tar $repo1

#Setup rhui20 directory
if [ ! -d /home/$userid/rhui20 ] ; then
    mkdir /home/$userid/rhui20
    tar -xvf /root/rhui202_installation.tar
    cp -R /root/$repo1/ans_dist_bkp /root/$repo1/gen_certs.tar /root/$repo1/extract_conf.sh /root/$repo1/hostname.sh /root/$repo1/install_rhui_iso.py /root/$repo1/reset.sh /root/$repo1/rhui_lib.py /root/$repo1/run_distribute.sh /root/$repo1/qpid_cert_gen.sh /root/$repo1/amazon_ec2_lib.py /root/$repo1/amazon_ec2.py /root/$repo1/ans_dist_bkp/host.sh /root/$repo1/ans_dist_bkp/answers_file /home/$userid/rhui20
else
    echo -e "\nrhui20 Directory already exists, skipping."
fi


[ ! -d /root/old-isotar ] && mkdir -p /root/old-isotar
pushd /home/$userid/rhui20 > /dev/null
mv /home/$userid/rhui20/rhui20-iso.tar /root/old-isotar/rhui20-iso-old-`date | awk -F" " '{print $4}'`.tar
mv ./rhui20-iso /tmp
popd > /dev/null

#Mount rhui-iso and create rhui-iso.tar excluding SRPMS.
[ ! -d /mnt/rhui-iso ] && mkdir -p /mnt/rhui-iso
umount /mnt/rhui-iso
iso_name=`echo "$iso_loc" | awk -F/ '{print $NF}'`
echo "iso name:" $iso_name
mount -t iso9660 -o loop $iso_loc /mnt/rhui-iso/ ; touch /home/$userid/rhui20/$iso_name
pushd /mnt/rhui-iso > /dev/null
tar --exclude=./SRPMS -cvf /home/$userid/rhui20/rhui20-iso.tar ./*
popd > /dev/null

pushd /home/$userid/rhui20 > /dev/null
mkdir rhui20-iso ; mv rhui20-iso.tar ./rhui20-iso
popd > /dev/null

pushd /home/$userid/rhui20/rhui20-iso > /dev/null
tar -xvf rhui20-iso.tar ; rm rhui20-iso.tar
popd > /dev/null

pushd /home/$userid/rhui20 > /dev/null
tar -cvf rhui20-iso.tar ./rhui20-iso
popd > /dev/null

#permission restore to that of the user.
chown -R  $userid.$userid /home/$userid/rhui20
chmod -R  755 /home/$userid/rhui20/rhui20-iso
