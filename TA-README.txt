### Guide to Getting the website Running ###

1. Go to the lab 2 folder

2. open terminal (IMPORTANT DO NOT SHUT DOWN THIS TERMINAL) & type:

$ python

$ import backend

$ resp = backend.create_service()

$ dns = backend.getdns(resp)

$ address = backend.staticip(resp,address)

$ print address

3. TA chmod 600 on your .pem key file

4. Open a new terminal and type :

Notes: 
	$1 - path to the .pem file
	$2 - path to my lab bottle folder
	$3 - dns value from the previous terminal

$ scp -r -i "$1/XXXXXXX.pem" $2/bottle-0.12.7 ubuntu@$3:

# now connect to the EC2 machine

$ ssh -i "$1/XXXXXXX.pem" ubuntu@$3

########## in EC2 #########################

$ cd bottle-0.12.7

$ sudo apt-get update

$ sudo python HelloWorld.py

5. get the ip address first terminal and enter to browser





