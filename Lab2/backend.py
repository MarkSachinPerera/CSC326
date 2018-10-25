import boto.ec2
import paramiko
import os
from paramiko import SSHClient

#set up
def create_service():
    conn = boto.ec2.connect_to_region("us-east-1")

    key_pair = conn.create_key_pair("security_key",dry_run=False)
    key_pair.save("/home/markperera/WorkSpace/WS-CSC326/Keys/")

    group = conn.create_security_group("basic_security", "The basic requirements for the lab")

    group.authorize("icmp", -1, -1, "0.0.0.0/0")
    group.authorize("tcp", 22, 22, "0.0.0.0/0")
#     group.authorize("icmp", 80, 80, "0.0.0.0/0")
    group.authorize("tcp", 80, 80, "0.0.0.0/0")

    resp = conn.run_instances("ami-9eaa1cf6", instance_type="t2.micro", key_name = "security_key", security_groups=[group])
    os.chmod("/home/markperera/WorkSpace/WS-CSC326/Keys/security_key.pem", 600)
    return resp

#doesnt do shit
def getState(resp):
    inst = resp.instances[0]
    update = inst.update()
    print update

#end the instances
def terminate(resp):
    conn = boto.ec2.connect_to_region("us-east-1")
    # resp = conn.get_all_instances()
    myid = resp.instances[0]
    myid = myid.id
    conn.terminate_instances(instance_ids=myid, dry_run=False)

#delete the ids
def cleanup():
    conn = boto.ec2.connect_to_region("us-east-1")
    conn.delete_security_group(name = "basic_security")
    conn.delete_key_pair("security_key")
    # conn.delete_security_group(name = "basic_security1")

    if os.path.exists("/home/markperera/WorkSpace/WS-CSC326/Keys/security_key.pem"):
        os.remove("/home/markperera/WorkSpace/WS-CSC326/Keys/security_key.pem")
    

#get the dns address for scp
def getdns(resp):
    inst = resp.instances[0]
    inst.update()
    ip = inst.ip_address
    dns = inst.dns_name
    print ip
    print dns
    return dns

#Associate IP address
def staticip(resp,address):
	conn = boto.ec2.connect_to_region("us-east-1")

	address = conn.allocate_address()
	inst = resp.instances[0]
	conn.associate_address(allocation_id = address.allocation_id, instance_id = inst.id )
	return address

def fileupload(resp,dns):
	ssh = paramiko.SSHClient()
	ssh.load_system_host_keys()
	ssh.connect(hostname = [dns], username= "ubuntu",  gss_trust_dns= True, key_filename= "/home/markperera/WorkSpace/WS-CSC326/Keys/security_key.pem")
	stdin, stdout, stderr = ssh.exec_command('ls -l')



# $ chmod 400 security_key
# $ ssh -i "security_key.pem" ubuntu@ec2-52-207-63-243.compute-1.amazonaws.com

#   SCP
# $ scp -r -i "security_key.pem" /home/markperera/WorkSpace/WS-CSC326/CSC326/bottle-0.12.7 ubuntu@ec2-52-207-63-243.compute-1.amazonaws.com:/
    
    
    # runSSH = paramiko.SSHClient()
    # runSSH.connect()



#   conn.delete_security_group(name = "basic_security")
#   conn.delete_key_pair("security_key")
#   terminate_instances(instance_ids=None, dry_run=False)
#   delete_security_group(name=None, group_id=None, dry_run=False)
#   get_key_pair(keyname, dry_run=False)
#   delete_key_pair(key_name, dry_run=False)