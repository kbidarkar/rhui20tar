#!/usr/bin/python -E
# Authors: Kedar Bidarkar <kbidarka@redhat.com>
#
# Copyright (C) 2011  Red Hat
# see file 'COPYING' for use and warranty information
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; version 2 only
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

try:
    import boto.ec2
except ImportError:
    print "Sorry, you don't have the boto module installed, and this"
    print "script relies on it.  Please install or reconfigure boto- 2.0b3"
    print "and try again."


import rhui_lib
import re
import time
import sys
import os
from subprocess import call



print "Fetching the regions :\n"
list_regions = boto.ec2.regions()

def refine_list(list_text):
    if hasattr(list_text, '__iter__'):
        for element in list_text:
            list_ele = str(element)
            matches1 = re.match(r'([\w.]+):([\w.-]+)', list_ele)
            if matches1: 
                reg1 = matches1.group(2)
                print reg1
    elif not hasattr(list_text, '__iter__'):
        str_ele = str(list_text)
        matches1 = re.match(r'([\w.]+):([\w.-]+)', str_ele)
        if matches1:
            reg1 = matches1.group(2)
            return reg1
    else:
        print "Will work only for list or string"

def refined_list(list_text):
    ref_list = []
    for element in list_text:
        list_ele = str(element)
        matches1 = re.match(r'([\w.]+):([\w.-]+)', list_ele)
        if matches1: 
            reg1 = matches1.group(2)
            ref_list.append(reg1)
    return ref_list
                 
def chek_null(var, prompt):
    while True:
        if var:
            return var
            break
        else:
            var = raw_input(prompt)
            continue
 
print "Following are the regions available :\n"
refine_list(list_regions)

region_name = None
region_name = chek_null(region_name, "\nPlease specify the Region name to connect : ")
connect_ec2 = boto.ec2.connect_to_region(region_name)
       
image_all = None
imag_ids = connect_ec2.get_all_images()
print "\nFollowing are the ec2-RHEL-images for the above selected region"
print "\nRHEL 6.2 Images\n\n"
for im in imag_ids:
    det = im.location
    if 'RHEL-6.2-Starter-EBS-x86_64' in str(det):
        det1 = im.location
        if 'Hourly2' or 'Access2' in str(det1):
            print im.id, im.location
image_all = chek_null(image_all, "\nPlease specify the common ami-id to be used for RHUA, CDS and Clients \n(e.g: [us-E] ami-7dea2614 / ) ami-id : ")
im_all = connect_ec2.get_image(image_all)
im_rhua = im_cds = im_client = im_all
print "\nFollowing is the image selected for launch:"
print refine_list(im_all)
print "\nFollowing is the information regarding the ami's :\n"
print refine_list(im_all), im_all.location       

    
key_nam = None
key_nam = chek_null(key_nam, "\nPlease specify the Key Name (e.g :- cloud-keyuswest-new) : ")

#Checking for all the files
home_dir = os.path.expanduser("~")
p1_file = key_nam + ".pem"
file_list = ['rhui20/extract_conf.sh','rhui20/rhui20-iso.tar',
'rhui20/answers_file', 'rhui20/gen_certs.tar', 'rhui20/run_distribute.sh',
'rhui20/host.sh', 'rhui20/hostname.sh', 'rhui20/qpid_cert_gen.sh']
file_list.append(p1_file)
list_sz = len(file_list)
rhui_lib.chek_files(file_list, list_sz)

# These three lines actually launch the instances. 
reg_name = region_name + 'b'  # Can provide ( 'a', 'b')
reservation_rhua = im_rhua.run(min_count='1', max_count='1', key_name=key_nam, placement=reg_name, security_groups=['RHUA Security Group'], instance_type='m1.large')
reservation_cds = im_cds.run(min_count='2', max_count='2', key_name=key_nam, placement=reg_name, security_groups=['CDS Security Group'], instance_type='m1.large')
reservation_client = im_client.run(min_count='1', max_count='1', key_name=key_nam, placement=reg_name, security_groups=['Client Security Group'], instance_type='m1.large')

username = 'root'
p_file = home_dir + "/" + key_nam + ".pem"   

def clean_inst(nod):
    for instance in nod.instances:
        instance.update()
        if instance.state == 'terminated':
            nod_inst = nod.instances
            nod_inst.remove(instance)
        elif instance.state == 'shutting-down':
            nod_inst = nod.instances
            nod_inst.remove(instance)

print "\n\nChecking the status of various instances : \n\n"  
def instance_stat(nod, pro):
    for instance in nod.instances:
        if len(nod.instances) == 8:
            print "Maximum tries exceeded. Please try manually"
            sys.exit()
        cnt = 0
        while cnt <= 4:
            instance.update()
            print "Status of " + pro + " Instance : ", refine_list(instance), "=>", instance.state
            if instance.state == 'running':
                break
            elif instance.state == 'pending':
                cnt = cnt + 1
                time.sleep(22)
                if cnt == 5:
                    print "More than 4 attempts made, for total 90 seconds. Terminating the instance and re-launching another one."
                    instance.terminate()   
                    nod_inst = nod.instances
                    reserve = im_all.run(min_count='1', max_count='1', key_name=key_nam, placement=reg_name, security_groups=[pro], instance_type='m1.large')
                    for res in reserve.instances:
                        nod_inst.append(res)
                    time.sleep(20)
            elif instance.state == 'terminated':
                break                   
                    
instance_stat(reservation_cds, "CDS Security Group")
instance_stat(reservation_client, "Client Security Group")
instance_stat(reservation_rhua, "RHUA Security Group")

# Cleaning the traces of terminated instances from the list of nodes.
clean_inst(reservation_cds)
clean_inst(reservation_client)
clean_inst(reservation_rhua)       

# Checking the status of private keys 
def keys_stat(nod, pro):
    print "\n\nChecking the " + pro + " instances keys_status by downloading a file\n\n"
    for instance in nod.instances:
        nod_inst = nod.instances
        host_auto = instance.dns_name
        l_path = home_dir + "/rhui20/network"
        f_path = "/etc/init.d/network"
        keystat = rhui_lib.getfile(host_auto, p_file, l_path, f_path)    
        if keystat:
            print "\n\nMore than 7 attempts made, for total 105 seconds. Terminating the instance and re-launching another one."
            instance.terminate()
            instance.update()
            print instance.state
            s_grp = pro + " Security Group"
            reserve = im_all.run(min_count='1', max_count='1', key_name=key_nam, placement=reg_name, security_groups=[s_grp], instance_type='m1.large')
            for instance1 in reserve.instances:
                if len(reserve.instances) == 8:
                    print "Maximum tries exceeded. Please try manually"
                    sys.exit()
                cnt = 0 
                while cnt <= 3:
                    instance1.update()
                    print "\nStatus of " + s_grp + " Instance : ", refine_list(instance1), "=>", instance1.state
                    if instance1.state == 'running':
                        nod_inst.append(instance1)
                        time.sleep(60)  
                        break
                    elif instance1.state == 'pending':
                        cnt = cnt + 1
                        print cnt
                        time.sleep(13)
                        if cnt == 4:
                            print "\nMore than 3 attempts made, for total 40 seconds. Terminating the instance and re-launching another one."
                            instance1.terminate()
                            res_inst =  reserve.instances
                            reserve1 = im_all.run(min_count='1', max_count='1', key_name=key_nam, placement=reg_name, security_groups=[s_grp], instance_type='m1.large')
                            for res in reserve1.instances:
                                res_inst.append(res)
                                time.sleep(30)
                    elif instance1.state == 'terminated':
                        break
                    elif instance1.state == 'shutting-down':
                        break
                       
keys_stat(reservation_cds, "CDS")
keys_stat(reservation_client, "Client")
keys_stat(reservation_rhua, "RHUA")

# Cleaning the traces of terminated instances from the list of nodes.         
clean_inst(reservation_cds)
clean_inst(reservation_client)
clean_inst(reservation_rhua)           

# To display the public and private DNS names   
def display_inst1(nod, otpt):
    sys.stdout.write("\n\n")
    sys.stdout.write(otpt)
    sys.stdout.write("\n\n")
    for instance in nod.instances:
        instance.update()
        print "Public DNS Name    : ", instance.dns_name
        print "Private DNS Name   : ", instance.private_dns_name, "\n" 
              
display_inst1(reservation_cds, "CDS Instances Information")
display_inst1(reservation_client, "Client Instances Information")
display_inst1(reservation_rhua, "RHUA Instance Information")
                        
#Create Volumes
cr_vol = []
no_vol = len(reservation_cds.instances) + len(reservation_rhua.instances)
for no_vol1 in range(no_vol):
    volm = connect_ec2.create_volume(100,reg_name)
    cr_vol.append(volm)
print "\n\nEBS Volumes Information\n"
for vol in cr_vol:
    print "The EBS volumes : ", vol.id

#Instance list, to which the Volumes need to be attached. ( vol_inst is list of instances)
vol_inst = []
for rcds in reservation_cds.instances:
    vol_inst.append(rcds)
for rrhua in reservation_rhua.instances:
    vol_inst.append(rrhua)
   
#Attach volumes ( As per the amazon the first device available for EBS is /dev/sdf)
#dev_ebs = None
#dev_ebs = chek_null(dev_ebs, "\nPlease specify the EBS Device that needs to be created (e.g: Starting from /dev/sdf to /dev/sdp) : ")
dev_ebs = "/dev/sdh"
for no in range(no_vol):
    vol1 = refine_list(cr_vol[no])
    inst1 = refine_list(vol_inst[no])
    volume_status = connect_ec2.attach_volume(vol1, inst1, dev_ebs)
    print "\n\nAttempting to attach volume ", vol1, " to instance : ", inst1    
    for tme in range(0, 7):
        sys.stdout.write('.')
        sys.stdout.flush()
        time.sleep(1)

#Verifying Attached Volumes
print "\n\n\nConfirming Volume status"
str_cr_vol = refined_list(cr_vol)
verify_attach_vol = connect_ec2.get_all_volumes(volume_ids=str_cr_vol)
for vl in verify_attach_vol:
    if vl.status == 'in-use':
        print "\nThis EBS Volume ", refine_list(vl), " is attached and in-use"
    elif vl.status == 'creating':
        print "\nThis EBS ", refine_list(vl), " is not attached and is being created"
    else:
        print "\nSeems to be some issue, Please check manually"
      
os.system("sh ~/rhui20/extract_conf.sh")

call(["cp", os.path.expanduser("~/rhui20/pulp.conf"), os.path.expanduser("~/rhui20/pulp1")]) 
call(["cp", os.path.expanduser("~/rhui20/cds.conf"), os.path.expanduser("~/rhui20/cds1")]) 
call(["cp", os.path.expanduser("~/rhui20/rhui-tools.conf"), os.path.expanduser("~/rhui20/rhui-tools1")])
call(["cp", os.path.expanduser("~/rhui20/answers_file"), os.path.expanduser("~/rhui20/answers_file1")])
call(["cp", os.path.expanduser("~/rhui20/run_distribute.sh"), os.path.expanduser("~/rhui20/run_distribute.sh.bkp")])
call(["cp", os.path.expanduser("~/rhui20/hostname.sh"), os.path.expanduser("~/rhui20/hostname.sh.bkp")])
call(["cp", os.path.expanduser("~/rhui20/host.sh"), os.path.expanduser("~/rhui20/host.sh.bkp")])

for instance1 in reservation_rhua.instances:
    host_pulp_srv = instance1.private_dns_name
    stext = "localhost"
    dtext = host_pulp_srv
    file_list_file = ['pulp.conf']
    for inpu in file_list_file:
        inpu_file = home_dir + "/rhui20/" + inpu
        rhui_lib.answers_replace(stext, dtext, inpu_file)
    stext = "localhost"
    dtext = host_pulp_srv
    inpu_file = home_dir + "/rhui20/rhui-tools.conf"
    rhui_lib.answers_replace(stext, dtext, inpu_file)

for instance in reservation_cds.instances:
    host_pulp_srv = instance1.private_dns_name
    stext = "localhost.localdomain"
    dtext = host_pulp_srv
    file_list_file = ['cds.conf']
    for inpu in file_list_file:
        inpu_file = home_dir + "/rhui20/" + inpu
        rhui_lib.answers_replace(stext, dtext, inpu_file)

os.system("pushd ~/rhui20 > /dev/null ; tar -cvf ~/rhui20/pulp_setup.tar pulp.conf cds.conf rhui-tools.conf ; popd > /dev/null")

hosts_dns1_name = []
for instance in reservation_cds.instances:
    dns1 = instance.private_dns_name
    hosts_dns1_name.append(dns1)
    
hosts_dns2_name = []
for instance in reservation_rhua.instances:
    dns2 = instance.private_dns_name
    hosts_dns2_name.append(dns2) 

def run_distribute_file(dist_file):
    p_file = home_dir + "/" + key_nam + ".pem"
    s_text = ['root@cds1', 'root@cds2']
    d_text = hosts_dns1_name
    inpu_file = home_dir + dist_file
    for no in range(2):
        stext = s_text[no]
        dtext = d_text[no]
        rhui_lib.answers_replace(stext, dtext, inpu_file)  
        
    s_text = ['root@rhua']
    d_text = hosts_dns2_name
    inpu_file = home_dir + dist_file
    for no in range(1):
        stext = s_text[no]
        dtext = d_text[no]
        rhui_lib.answers_replace(stext, dtext, inpu_file)  
       
    stext = "cloud_key"
    dtext = "/root/" + key_nam + ".pem"
    rhui_lib.answers_replace(stext, dtext, inpu_file)
        
    print "\n\nWorking again with RHUA instance to upload the updated", inpu_file, " file"   
    for instance in reservation_rhua.instances:
        host_auto = instance.dns_name
        command = 'mkdir -p /root/rhui20'
        print "\nInstalling various rpms: \n", command
        rhui_lib.remote_exe(host_auto, p_file, command)
        l_path = home_dir + dist_file
        f_path = "/root" + dist_file
        rhui_lib.putfile(host_auto, p_file, l_path, f_path)
        
run_distribute_file("/rhui20/host.sh")


#Putting all the required files in the instances
print "\n\nWorking with RHUA instance"
for instance in reservation_rhua.instances:
    host_auto = instance.dns_name
    l_path = home_dir + "/rhui20/pulp_setup.tar"
    f_path = "/root/pulp_setup.tar"
    rhui_lib.putfile(host_auto, p_file, l_path, f_path)
    l_path = home_dir + "/rhui20/qpid_cert_gen.sh"
    f_path = "/root/qpid_cert_gen.sh"
    rhui_lib.putfile(host_auto, p_file, l_path, f_path)
#For security reasons avoid transfering your private key to the host, 
#if transfered for any reasons **DO NOT** enable password authentication.
    l_path = p_file
    f_path = "/root/" + key_nam + ".pem"
    rhui_lib.putfile(host_auto, p_file, l_path, f_path)
    command = "chmod 600 /root/" + key_nam + ".pem"
    print "\nChange key Permissions : \n", command
    rhui_lib.remote_exe(host_auto, p_file, command)

    l_path = home_dir + "/rhui20/hostname.sh"
    f_path = "/root/hostname.sh"
    rhui_lib.putfile(host_auto, p_file, l_path, f_path)      
    l_path = home_dir + "/rhui20/gen_certs.tar"
    f_path = "/root/gen_certs.tar"
    rhui_lib.putfile(host_auto, p_file, l_path, f_path)  
    l_path = home_dir + "/rhui20/rhui20-iso.tar"
    f_path = "/root/rhui20-iso.tar"
    rhui_lib.putfile(host_auto, p_file, l_path, f_path)  
    #Connecting to the rhua instance and formatting the devices (e.g : /dev/sdf)
    command = 'tar -xvf /root/pulp_setup.tar ; tar -xvf /root/gen_certs.tar ; tar -xvf /root/rhui20-iso.tar ; iptables -F'
    print "\nUntaring the Pulp tar files : \n", command
    rhui_lib.remote_exe(host_auto, p_file, command)
#    command = '/bin/rpm -Uvh http://download.fedora.redhat.com/pub/epel/beta/6/i386/epel-release-6-5.noarch.rpm'
#    print "\nInstalling epel-release rpm: \n", command
#    rhui_lib.remote_exe(host_auto, p_file, command)
#Connecting to the rhua instance and formatting the devices (e.g : /dev/sdf)
    command = 'mkfs.ext3 /dev/xvdl ; mkdir -p /var/lib/pulp ; chown apache.apache /var/lib/pulp ; chmod g+ws,o+t /var/lib/pulp ; mount -t ext3 /dev/xvdl /var/lib/pulp'
    print "\n\nCreating the directory structure: \n", command
    rhui_lib.remote_exe(host_auto, p_file, command)       
    command = 'yum install wget screen vpnc -y'
    print "\nInstalling various rpms: \n", command
    rhui_lib.remote_exe(host_auto, p_file, command)
    command = '/bin/sh /root/hostname.sh'
    print "\nRenaming the Hostnames: \n", command
    rhui_lib.remote_exe(host_auto, p_file, command)  
    command = 'pushd /root/rhui20-iso > /dev/null ; ./install_RHUA.sh ; ./install_tools.sh ; popd > /dev/null'
    print "\nInstalling PULP and RHUI rpms: \n", command
    rhui_lib.remote_exe(host_auto, p_file, command)
    command = "cp /root/pulp.conf /etc/pulp/ ; mkdir -p /root/rhui20"
    print "\nPlacing the pulp.conf and client.conf file to desired location : \n", command
    rhui_lib.remote_exe(host_auto, p_file, command)
    command = "cp /root/rhui-tools.conf /etc/rhui/"
    print "\nPlacing the rhui-tools.conf file to desired location : \n", command
    rhui_lib.remote_exe(host_auto, p_file, command)
    command = 'service pulp-server init ; service pulp-server start'
    print "\nStarting the Pulp server service : \n", command
    rhui_lib.remote_exe(host_auto, p_file, command) 
    
    print "Creating the RHUA SSL certs"
    rhua_crt_name = []
    for insta1 in reservation_rhua.instances:
#       command = "/root/gen_certs/gen.sh" + " rhua"+refine_list(insta1)+".crt " + "`hostname`"
        command = "/root/gen_certs/gen2.sh" + " rhua"+refine_list(insta1)+".crt " + insta1.private_dns_name
        print "\nGenerating SSL certificate for RHUA instance : ", refine_list(insta1)
        print "Running :" + command
        rhui_lib.remote_exe(host_auto, p_file, command)
        rhua_crt = "/root/gen_certs/build/rhua"+refine_list(insta1)+".crt"
        rhua_crt_name.append(rhua_crt) 
         
        
    print "Creating the CDS SSL certs"
    cds_num = 1
    serial_num = 06
    serial_num = serial_num + 1
    cds_crt_names = []
    for insta2 in reservation_cds.instances:
#        command = "/root/gen_certs/gen.sh" + " cds"+str(cds_num)+refine_list(insta2)+".crt " + "`hostname`"
        command = "cp /root/gen_certs/gen1.sh /root/gen_certs/gen1.sh.bkp ; sed -i s/06/0"+str(serial_num)+"/ /root/gen_certs/gen1.sh ; /root/gen_certs/gen1.sh" + " cds"+str(cds_num)+refine_list(insta2)+".crt " + insta2.private_dns_name
        print "\nGenerating SSL certificate for CDS instance : ", refine_list(insta2)
        print "Running :" + command
        rhui_lib.remote_exe(host_auto, p_file, command)
        command = "mv /root/gen_certs/gen1.sh.bkp /root/gen_certs/gen1.sh"
        rhui_lib.remote_exe(host_auto, p_file, command)
        cds_crt = "/root/gen_certs/build/cds"+str(cds_num)+refine_list(insta2)+".crt"
        cds_crt_names.append(cds_crt) 
        cds_num = cds_num + 1  
        serial_num = serial_num + 1 
        
hosts_dns_name = []
for instance in reservation_rhua.instances:
    dns1 = instance.private_dns_name
    hosts_dns_name.append(dns1)
#dns = proxy_inst.private_dns_name
#hosts_dns_name.append(dns)
for instance in reservation_cds.instances:
    dns1 = instance.private_dns_name
    hosts_dns_name.append(dns1)
    
ssl_certs = []
for sslc in rhua_crt_name:
    ssl_certs.append(sslc)
for sslc in cds_crt_names:
    ssl_certs.append(sslc)

def answers_file(ans_file):
    s_text = ['rhua.example.com', 'cds1.example.com', 'cds2.example.com']
    d_text = hosts_dns_name
    inpu_file = home_dir + ans_file
    for no in range(3):
        stext = s_text[no]
        dtext = d_text[no]
        rhui_lib.answers_replace(stext, dtext, inpu_file)  
       
    s_text = ['rhua.crt', 'cds1.crt', 'cds2.crt']
    d_text = ssl_certs
    for no in range(3):
        stext = s_text[no]
        dtext = d_text[no]
        rhui_lib.answers_replace(stext, dtext, inpu_file)
        
    print "\n\nWorking again with RHUA instance to upload the updated answers.sample file"
    p_file = home_dir + "/" + key_nam + ".pem"   
    for instance in reservation_rhua.instances:
        host_auto = instance.dns_name
        l_path = home_dir + ans_file
        f_path = "/root" + ans_file
        rhui_lib.putfile(host_auto, p_file, l_path, f_path)
        
answers_file("/rhui20/answers_file")

run_distribute_file("/rhui20/run_distribute.sh")



print "\n\nWorking with CDS instance"
for instance in reservation_cds.instances:
    host_auto = instance.dns_name
    l_path = home_dir + "/rhui20/pulp_setup.tar"
    f_path = "/root/pulp_setup.tar"
    rhui_lib.putfile(host_auto, p_file, l_path, f_path)
#For security reasons avoid transfering your private key to the host, 
#if transfered for any reasons **DO NOT** enable password authentication to this host.
    l_path = p_file
    f_path = "/root/" + key_nam + ".pem"
    rhui_lib.putfile(host_auto, p_file, l_path, f_path) 
    l_path = home_dir + "/rhui20/hostname.sh"
    f_path = "/root/hostname.sh"
    rhui_lib.putfile(host_auto, p_file, l_path, f_path)      
    l_path = home_dir + "/rhui20/rhui20-iso.tar"
    f_path = "/root/rhui20-iso.tar"
    rhui_lib.putfile(host_auto, p_file, l_path, f_path)  
    #Connecting to the rhua instance and formatting the devices (e.g : /dev/sdf)
    command = "chmod 600 /root/" + key_nam + ".pem"
    print "\nChange key Permissions : \n", command
    rhui_lib.remote_exe(host_auto, p_file, command)

    command = 'tar -xvf /root/pulp_setup.tar ; tar -xvf /root/rhui20-iso.tar ; iptables -F'
    print "\nUntaring the Pulp tar files : \n", command
    rhui_lib.remote_exe(host_auto, p_file, command)

#    command = '/bin/rpm -Uvh http://download.fedora.redhat.com/pub/epel/beta/6/i386/epel-release-6-5.noarch.rpm'
#    print "\nInstalling epel-release rpm: \n", command
#    rhui_lib.remote_exe(host_auto, p_file, command)
#Connecting to the rhua instance and formatting the devices (e.g : /dev/sdf)
    command = 'mkfs.ext3 /dev/xvdl ; mkdir -p /var/lib/pulp-cds ; mount -t ext3 /dev/xvdl /var/lib/pulp-cds'
    print "\n\nCreating the directory structure: \n", command
    rhui_lib.remote_exe(host_auto, p_file, command)       
    command = 'yum install wget screen vpnc -y'
    print "\nInstalling PULP CDS rpms: \n", command
    rhui_lib.remote_exe(host_auto, p_file, command)
    command = '/bin/sh /root/hostname.sh'
    print "\nRenaming the Hostnames: \n", command
    rhui_lib.remote_exe(host_auto, p_file, command)  
    command = 'pushd /root/rhui20-iso > /dev/null ; ./install_CDS.sh ; popd > /dev/null'
    print "\nInstalling PULP CDS rpms: \n", command
    rhui_lib.remote_exe(host_auto, p_file, command)
    command = "cp /root/cds.conf /etc/pulp/"
    print "\nPlacing the cds.conf file to desired location : \n", command
    rhui_lib.remote_exe(host_auto, p_file, command)
    command = 'service pulp-cds start'
    print "\nStarting the Pulp cds service : \n", command
    rhui_lib.remote_exe(host_auto, p_file, command) 
    
for instance in reservation_rhua.instances:
    host_auto = instance.dns_name
    command = '/bin/sh /root/rhui20/host.sh'
    print "\nPopulating the /etc/hosts file: \n", command
    rhui_lib.remote_exe(host_auto, p_file, command)     
    command = '/usr/bin/expect /root/qpid_cert_gen.sh'
    print "\nQpid_cert_generation: \n", command
    rhui_lib.remote_exe(host_auto, p_file, command)     
    command = '/bin/sh /root/rhui20/run_distribute.sh'
    print "\nInstalling rhua and cds rpms: \n", command
    rhui_lib.remote_exe(host_auto, p_file, command)     

call(["mv", os.path.expanduser("~/rhui20/pulp1"), os.path.expanduser("~/rhui20/pulp.conf")]) 
call(["mv", os.path.expanduser("~/rhui20/cds1"), os.path.expanduser("~/rhui20/cds.conf")]) 
call(["mv", os.path.expanduser("~/rhui20/rhui-tools1"), os.path.expanduser("~/rhui20/rhui-tools.conf")])
call(["mv", os.path.expanduser("~/rhui20/answers_file1"), os.path.expanduser("~/rhui20/answers_file")])
call(["mv", os.path.expanduser("~/rhui20/run_distribute.sh.bkp"), os.path.expanduser("~/rhui20/run_distribute.sh")])
call(["mv", os.path.expanduser("~/rhui20/hostname.sh.bkp"), os.path.expanduser("~/rhui20/hostname.sh")])
call(["mv", os.path.expanduser("~/rhui20/host.sh.bkp"), os.path.expanduser("~/rhui20/host.sh")])
os.system("rm -f ~/rhui20/network ~/rhui20/pulp.conf ~/rhui20/cds.conf ~/rhui20/rhui-tools.conf")

display_inst1(reservation_cds, "CDS Instances Information")
display_inst1(reservation_client, "Client Instances Information")
display_inst1(reservation_rhua, "RHUA Instance Information")
