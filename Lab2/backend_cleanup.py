import boto.ec2

conn = boto.ec2.connect_to_region("us-east-1")

conn.delete_security_group(name = "basic_security")
conn.delete_key_pair("security_key")