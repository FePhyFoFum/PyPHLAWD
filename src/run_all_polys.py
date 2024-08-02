import sys
import os

import tree_reader
import node
import seq

ogdb = "../../api.db"
ogf = "../../gzzsseqs/apigzseqs/"

cmd0 = "python ~/apps/PyPHLAWD/src/combine_datasets.py "
cmd3 = "python ~/apps/PyPHLAWD/src/add_outgroup_to_matrix.py -b "+ogdb+" -m MATRIX -p PART -t TAX -o OUT -s"+ogf
cmd4 = "iqtree -m GTR+G -s ALN -q PART -nt 4 -g CONS -redo " 
cmd5 = "raxml -m GTRCAT -T 2 -g CONS -s ALN -p 12345 -n RAXRUN"
fn = "_outaln"
cmb1 = "TEMPTEMPCAT"
cmb2 = "TEMPTEMPPART"

def get_constraint(nms,tre):
    keep = []
    todel= []
    for i in tre.iternodes():
        if i.label in nms:
            keep.append(i)
            continue
        if len(set([k.label for k in i.iternodes()]).intersection(set(nms))) == 0:
            todel.append(i)
    for i in todel:
        p = i.parent
        p.remove_child(i)
    # remove knuckles
    going = True
    while going:
        going = False
        for i in tre.iternodes():
            if len(i.children) == 1:
                going = True
                if i.parent == None:
                    tre = i.children[0]
                    break
                else:
                    p = i.parent
                    p.add_child(i.children[0])
                    p.remove_child(i)
    return tre

def add_outgroup_constraint_write(cont,og):
    nd2 = node.Node()
    nd2.label = og
    cont.add_child(nd2)
    for i in cont.leaves():
        i.label=i.label.split("_")[-1]
    fl = open("CONSTRAINT","w")
    fl.write(cont.get_newick_repr(False)+";")
    fl.close()
    return "CONSTRAINT"

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("python",sys.argv[0],"treefile maindir outgroup")
        sys.exit(0)
    tf = sys.argv[1]
    md = sys.argv[2]
    og = sys.argv[3]
    if md[-1] != "/":
        md += "/"
    t = tree_reader.read_tree_file_iter(tf).__next__()
    count = 0
    for i in t.iternodes("preorder"):
        if len(i.children) >= 3:
            tff = "poly."+str(count)+".treefile"
            if os.path.isfile(tff):
                count += 1
                continue
            t2 = tree_reader.read_tree_file_iter(tf).__next__()
            chds = [] #intended to have the ids of what we will look for in the directories
            stack = [j for j in i.children]
            while len(stack) > 0:
                p = stack.pop()
                if p.label != "":
                    chds.append(p)
                    continue
                else:
                    for j in p.children:
                        stack.append(j)
            labs = [j.label for j in chds]
            print("- "+" ".join(labs))
            dirs = []
            for j in labs:
                jl = j.split("_")[-1]
                mdjl = md+jl+"_"+jl
                if os.path.exists(mdjl):
                    dirs.append(mdjl+"/"+jl+"_"+jl+fn)
            cmd = cmd0+" ".join(dirs)
            print(cmd)
            os.system(cmd)
            tips = set(seq.read_fasta_file_return_dict("TEMPTEMPCAT").keys())
            if len(tips) == 0:
                continue
            labs = [j for j in labs if j.split("_")[-1] in tips]
            if len(labs) < 3:
                continue
            cont = get_constraint(labs,t2)
            cmd = cmd3.replace("MATRIX",cmb1).replace("PART",cmb2).replace("TAX",og).replace("OUT",cmb1+".og")
            print(cmd)
            os.system(cmd)
            tb = "TEMPTEMPCAT.og.table"
            og = ""
            f = open(tb,"r")
            for j in f:
                og = j.strip().split("\t")[1]
                break
            f.close()
            fln = add_outgroup_constraint_write(cont,og)
            mv1 = "TEMPTEMPCAT.og.outaln"
            mv2 = "TEMPTEMPCAT.og.outpart"
            #cmd = cmd4.replace("ALN",mv1).replace("PART",mv2).replace("CONS",fln)
            cmd = cmd5.replace("ALN",mv1).replace("CONS",fln)
            print(cmd)
            os.system(cmd)
            tff = "RAxML_bestTree.RAXRUN"
            os.system("mv "+mv1+" poly."+str(count)+".outaln")
            os.system("mv "+mv2+" poly."+str(count)+".outpart")
            os.system("mv "+tff+" poly."+str(count)+".treefile")
            tff = "poly."+str(count)+".treefile"
            os.system("pxrr -t "+tff+" -g "+og+" > "+tff+".rr")
            rm1 = "TEMPTEMPCAT.og.tempdbfa*"
            rm2 = "RAxML*"
            #rm2 = "TEMPTEMPCAT.og.outpart.*"
            os.system("rm "+rm1)
            os.system("rm "+ rm2)
            count += 1
            
