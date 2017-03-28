"""
this does the cluster single for the tips
"""
import sys
import os

DI = "~/Dropbox/programming/python/pyphlawd/"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "python "+sys.argv[0]+" startdir"
        sys.exit(0)
    root = sys.argv[1]
    for dirn, subdl, filel in os.walk(root,topdown=False):
        if len(subdl) == 1:
            if subdl[0] == "clusters":
                print "clustering",dirn
                cmd = "python "+DI+"cluster_single.py "+dirn
                os.system(cmd)
