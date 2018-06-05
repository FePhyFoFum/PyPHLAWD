import os
import sys
import random
from clint.textui import colored
import subprocess

from conf import DI
from conf import treemake
import emoticons
from logger import Logger
import tree_reader

def run_tree(infile,outfile):
    cmd = "FastTree -nt -gtr "+infile+" 2>fasttree.out > "+outfile
    os.system(cmd)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "python "+sys.argv[0]+" startdir logfile"
        sys.exit(0)
    
    root = sys.argv[1]
    logfile = sys.argv[2]
    log = Logger(logfile)
    # get the random directory so you can run multiple things in the same directory
    rantempdir = "TEMPDIR_"+str(random.randint(0,100000))+"/"
    print colored.blue("CREATED"),rantempdir
    os.mkdir(rantempdir)
    log.wac("CREATED "+rantempdir)
    count = 0
    for root, dirs, files in os.walk(root,topdown=False):
        if "clusters" not in root:
            log.whac(root)
            if len(dirs) == 1:
                print colored.yellow("CLUSTERING SINGLE"),root,colored.yellow(emoticons.get_ran_emot("meh"))
                log.wac("CLUSTERING SINGLE "+root)
                tablename = [x for x in files if ".table" in x][0]
                cmd = "python "+DI+"cluster_single.py "+root+" "+logfile
                os.system(cmd)
            else:
                print colored.blue("CLUSTERING INTERNAL"),root,colored.blue(emoticons.get_ran_emot("meh"))
                log.wac("CLUSTERING INTERNAL "+root)
                tablename = [x for x in files if ".table" in x][0]
                if root[-1] != "/":
                    root = root+"/"
                cmd = "python "+DI+"cluster_internal.py "+root+ " "+root+tablename+" "+logfile+" "+rantempdir
                rc = subprocess.call(cmd,shell=True)
                if rc != 0:
                    print colored.red("PROBLEM WITH CLUSTERING INTERNAL"),colored.red(emoticons.get_ran_emot("sad"))
                    sys.exit(1)
    cmd = "python "+DI+"annotate_clusters.py "+sys.argv[1]
    os.system(cmd)
    cmd = "python "+DI+"post_process_cluster_info.py "+sys.argv[1]
    os.system(cmd)
    
