import sys
sys.path.insert(0,"Lab2/")
import backend as bk
import time

def main():

    if len(sys.argv) < 2:
        print "Usage: python create_aws.py security_key"
        exit (1)


    # resp = bk.create_from_user_key(sys.argv[1])
    time.sleep(60)
    dns = bk.getdns(resp)
    id = bk.get_instance_id(resp)

    print dns
    print id
    # print sys.argv[1]
    # print "hello"
    

if __name__ == "__main__":
    main()
