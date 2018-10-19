import boto.ec2


def create_service():
    conn = boto.ec2.connect_to_region("us-east-1")

    conn.create_key_pair("security_key",dry_run=False)

    group = conn.create_security_group("basic_security", "The basic requirements for the lab")

    group.authorize("icmp", -1, -1, "0.0.0.0/0")
    group.authorize("tcp", 22, 22, "0.0.0.0/0")
    group.authorize("icmp", 80, 80, "0.0.0.0/0")

    resp = conn.run_instances("ami-9eaa1cf6", instance_type="t2.micro", key_name = "security_key", security_groups=[group])

    return resp

def getState(resp):

    inst = resp.instances[0]
    inst.update()

def terminate(resp):
    conn = boto.ec2.connect_to_region("us-east-1")
    # resp = conn.get_all_instances()
    myid = resp.instances[0]
    myid = myid.id
    conn.terminate_instances(instance_ids=myid, dry_run=False)


def cleanup():
    conn = boto.ec2.connect_to_region("us-east-1")
    conn.delete_security_group(name = "basic_security")
    conn.delete_key_pair("security_key")





#   conn.delete_security_group(name = "basic_security")
#   conn.delete_key_pair("security_key")
#   terminate_instances(instance_ids=None, dry_run=False)
#   delete_security_group(name=None, group_id=None, dry_run=False)
#   get_key_pair(keyname, dry_run=False)
#   delete_key_pair(key_name, dry_run=False)