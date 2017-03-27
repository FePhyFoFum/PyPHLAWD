import os
import sys
import tree_reader
from get_subset_genbank import make_files_with_id as mfid
from get_subset_genbank import make_files_with_id_justtable as mfid_justtable

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print "python "+sys.argv[0]+" tree dir DB"
        sys.exit(0)
    
    tree = tree_reader.read_tree_file_iter(sys.argv[1]).next()
    dirl = sys.argv[2]
    if dirl[-1] != "/":
        dirl = dirl + "/"
    DB = sys.argv[3]
    
    for i in tree.iternodes():
        if "unclassified" in i.label:
            continue
        if "environmental" in i.label:
            continue
        orig = i.label
        if i != tree:
            i.label = i.parent.label+"/"+i.label
        tid = orig.split("_")[1]
        dirr = i.label
        if len(i.children) == 0:
            mfid(tid,DB,dirl+dirr+"/"+orig+".fas",dirl+dirr+"/"+orig+".table",True) 
        else:
            mfid(tid,DB,dirl+dirr+"/"+orig+".fas",dirl+dirr+"/"+orig+".table",True) 
