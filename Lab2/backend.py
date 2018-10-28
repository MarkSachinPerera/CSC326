import boto.ec2
import paramiko
import os
from paramiko import SSHClient

#set up
def create_service():
    conn = boto.ec2.connect_to_region("us-east-1")

    # key_pair = conn.create_key_pair("xxxxxxxxxxx",dry_run=False)
    # key_pair.save("/home/markperera/WorkSpace/WS-CSC326/Keys/")

    group = conn.create_security_group("basic_security", "The basic requirements for the lab")

    group.authorize("icmp", -1, -1, "0.0.0.0/0")
    group.authorize("tcp", 22, 22, "0.0.0.0/0")
#     group.authorize("icmp", 80, 80, "0.0.0.0/0")
    group.authorize("tcp", 80, 80, "0.0.0.0/0")

    resp = conn.run_instances("ami-9eaa1cf6", instance_type="t2.micro", key_name = "xxxxxxxxxxx", security_groups=[group])
    os.chmod("xxxxxxxxxxx.pem", 600)
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
    conn.delete_key_pair("xxxxxxxxxxx")
    # conn.delete_security_group(name = "basic_security1")

    if os.path.exists("/home/markperera/WorkSpace/WS-CSC326/Keys/xxxxxxxxxxx.pem"):
        os.remove("/home/markperera/WorkSpace/WS-CSC326/Keys/xxxxxxxxxxx.pem")
    

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


