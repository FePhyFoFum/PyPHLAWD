import os
import sys
import subprocess
import random # for temp directory
import tree_reader
import emoticons
from clint.textui import colored
from logger import Logger
from conf import DI
from conf import py
from add_clade_clusters import make_blast_db_from_cluster

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("python "+sys.argv[0]+" startdir baitdir logfile")
        sys.exit(0)
    
    root = sys.argv[1]
    logfile = sys.argv[3]
    log = Logger(logfile)
    # get the random directory so you can run multiple things in the same directory
    rantempdir = "TEMPDIR_"+str(random.randint(0,100000))+"/"
    print(colored.blue("CREATED"),rantempdir)
    os.mkdir(rantempdir)
    log.wac("CREATED "+rantempdir)
    #prepare bait
    baitdir = sys.argv[2]
    # could do samp
    make_blast_db_from_cluster(baitdir,rantempdir)
    count = 0
    for root, dirs, files in os.walk(root,topdown=False):
        if "clusters" not in root:
            log.whac(root)
            if len(dirs) == 1:
                print(colored.yellow("BAIT SINGLE"),root,colored.yellow(emoticons.get_ran_emot("meh")))
                log.wac("BAIT SINGLE "+root)
                tablename = [x for x in files if ".table" in x][0]
                cmd = py+" "+DI+"bait_single.py "+root+" "+logfile+" "+rantempdir
                os.system(cmd)
            else:
                print(colored.blue("BAIT INTERNAL"),root,colored.blue(emoticons.get_ran_emot("meh")))
                log.wac("BAIT "+root)
                tablename = [x for x in files if ".table" in x][0]
                if root[-1] != "/":
                    root = root+"/"
                cmd = py+" "+DI+"bait_clade.py "+root+ " "+root+tablename+" "+logfile+" "+rantempdir
                rc = subprocess.call(cmd,shell=True)
                if rc != 0:
                    print(colored.red("PROBLEM WITH CLUSTERING INTERNAL"),colored.red(emoticons.get_ran_emot("sad")))
                    sys.exit(1)
    cmd = py+" "+DI+"annotate_clusters.py "+sys.argv[1]
    os.system(cmd)
    cmd = py+" "+DI+"post_process_cluster_info.py "+sys.argv[1]
    os.system(cmd)
    
