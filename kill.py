import sys
sys.path.insert(0,"Lab2/")
import backend as bk
import time

def main():
    if len(sys.argv) < 2:
        print "Usage: python kill.py id"
        exit (1)
    
    bk.terminate_from_id(sys.argv[1])

if __name__ == "__main__":
    main()