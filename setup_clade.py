import os
import sys
import tree_reader
from clint.textui import colored

DI = "~/Dropbox/programming/python/pyphlawd/"

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print "python "+sys.argv[0]+" taxon db dirl"
        sys.exit(0)
    
    dirl = sys.argv[3]
    if dirl[-1] == "/":
        dirl = dirl[:-1]
    taxon = sys.argv[1]
    db = sys.argv[2]
    tname = dirl+"/"+taxon+".tre"
    cmd = "python "+DI+"get_ncbi_tax_tree_no_species.py "+taxon+" "+db+" > "+tname
    print cmd
    os.system(cmd)
    trn = tree_reader.read_tree_file_iter(tname).next().label
    cmd = "python "+DI+"make_dirs.py "+tname+" "+dirl
    print cmd
    os.system(cmd)
    cmd = "python "+DI+"populate_dirs_first.py "+tname+" "+dirl+" "+db
    print cmd
    os.system(cmd)

