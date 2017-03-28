import os
import sys
import tree_reader
from clint.textui import colored
from logger import Logger
from conf import DI
from add_clade_clusters import make_blast_db_from_cluster

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print "python "+sys.argv[0]+" startdir baitdir logfile"
        sys.exit(0)
    
    root = sys.argv[1]
    logfile = sys.argv[3]
    log = Logger(logfile)
    #prepare bait
    baitdir = sys.argv[2]
    # could do samp
    make_blast_db_from_cluster(baitdir)
    count = 0
    for root, dirs, files in os.walk(root,topdown=False):
        if "clusters" not in root:
            log.whac(root)
            if len(dirs) == 1:
                print colored.yellow("BAIT SINGLE"),root
                log.wac("BAIT SINGLE "+root)
                tablename = [x for x in files if ".table" in x][0]
                cmd = "python "+DI+"bait_single.py "+root+" "+logfile
                os.system(cmd)
            else:
                print colored.blue("BAIT INTERNAL"),root
                log.wac("BAIT "+root)
                tablename = [x for x in files if ".table" in x][0]
                if root[-1] != "/":
                    root = root+"/"
                cmd = "python "+DI+"bait_clade.py "+root+ " "+root+tablename+" "+logfile
                os.system(cmd)
    cmd = "python "+DI+"annotate_clusters.py "+sys.argv[1]
    os.system(cmd)
    
