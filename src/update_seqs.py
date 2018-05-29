import sys
import os
import time

import node
from get_subset_genbank import make_files_with_id as mfid
from get_subset_genbank import make_files_with_id_internal as mfid_internal

"""
this will add new sequences to a directory. this can be used for updating but assumes
that the taxonomy has not changed so radically to render the folder useless
"""
# outfilehead is going to be a date,time stamp, tid is the id of the taxon, dirl is the directory, internal is whether it is internal
def add_updated_seqs_to_dir(dirl,tid,DB,outfilehead,internal = False):
    print dirl
    oldids = set()
    maintablename = None
    for i in os.listdir(dirl):
        # get the main table name so that we can update things
        if i[-len(".table"):] == ".table":
            maintablename = i
        # read all the tables
        if ".table" in i:
            print >> sys.stderr, "reading:",i
            fl = open(dirl+i,"r")
            for j in fl:
                spls = j.strip().split("\t")
                oldids.add(spls[2])
            fl.close()
    
    newids = set()
    newid_info = {} #key is id, value is full bit
    newid_seq = {} #key is id, value is seq
    seqs,tbls = None,None
    if internal == False:
        seqs,tbls = mfid(tid,DB,None,None)
    else:
        seqs,tbls = mfid_internal(tid,DB,None,None)
    for i,j in zip(seqs,tbls):
        spls = j.split("\t")
        newids.add(spls[2])
        newid_info[spls[2]] = j
        newid_seq[spls[2]] = i

    diff = newids.difference(oldids)
    if len(diff) > 0:    
        newtable = dirl+maintablename+"."+outfilehead
        newseqfn = dirl+maintablename.replace(".table",".fas")+"."+outfilehead
        print >> sys.stderr, "writing:",newtable
        print >> sys.stderr, "writing:",newseqfn
        newtablef = open(newtable,"w")
        newseqf = open(newseqfn,"w")
        for i in diff:
            newtablef.write(newid_info[i]+"\n")
            newseqf.write(newid_seq[i]+"\n")
        newtablef.close()
        newseqf.close()
    else:
        print >> sys.stderr,"no update"

# outfilehead is the part after the taxon that you want to distinguish the update. 
# I would base this on time with this command time.strftime("%m_%d_%Y_%H_%M_%S")

# if you do this from main it will do the whole tree
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "python "+sys.argv[0]+" base_dir DB"
        sys.exit(0)
    
    dirl = sys.argv[1]
    if dirl[-1] != "/":
        dirl = dirl + "/"

    tid = dirl.split("_")[-1][:-1]

    DB = sys.argv[2]

    outfh = str(time.strftime("%m_%d_%Y_%H_%M_%S"))

    nds = {} # dir,node
    nd = node.Node()
    nd.label = tid
    nd.data["tid"] = tid
    nd.data["dir"] = dirl
    nds[dirl[:-1]] = nd
    rootnd = nd
    for root,dirs,files in os.walk(dirl):
        if "clusters" in root:
            continue
        # assumes name_id
        tid = root.split("_")[-1]
        try:
            int(tid)
        except:
            continue
        nd = node.Node()
        nd.label = tid
        nd.data["tid"] = tid
        nd.data["dir"] = root+"/"
        nd.parent = nds["/".join(root.split("/")[:-1])]
        nd.parent.add_child(nd)
        nds[root] = nd
    
    for n in rootnd.iternodes(order="POSTORDER"):
        tid,dirl = n.data["tid"],n.data["dir"]
        print >> sys.stderr, tid,dirl
        internal = False
        if len(n.children) > 0:
            internal = True
        add_updated_seqs_to_dir(dirl,tid,DB,outfh,internal)
    