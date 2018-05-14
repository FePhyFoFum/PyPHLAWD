import sys
import os
import shlex
import subprocess
import check_for_programs
from conf import DI
from conf import relcut
from conf import abscut
from conf import usecython
from conf import smallest_cluster
from conf import cluster_prop
import emoticons
from clint.textui import colored
if usecython:
    import cnode as node
else:
    import node

"""
this assumes that you have already run 
post_process_cluster_info.py startdir
"""

mat_nms = []
clusterind = {}
keepers = set()#node

def record_info_table(infilecsv):
    tf = open(infilecsv,"r")
    mat = []
    #transpose the matrix
    first = True
    for i in tf:
        spls = i.strip().split(",")
        if len(spls) == 1:
            continue
        if first == True:
            first = False
            count = 0
            for j in spls[1:]:
                clusterind[count] = j
                mat.append(0)
                mat_nms.append([])
                count += 1
        else:
            count = 0
            for j in spls[1:]:
                if j == "x":
                    mat[count] += 1
                    mat_nms[count].append(spls[0])
                count += 1
    tf.close()

def check_info_table(tree):
    for i in tree.iternodes(order="POSTORDER"):
        if "names" not in i.data:
            continue
        if i.parent != None:
            for j in clusterind:
                inter = set(i.data["names"]).intersection(set(mat_nms[j]))
                pinter = set(i.parent.data["names"]).intersection(set(mat_nms[j]))
                if len(inter) > 0 and len(pinter) == len(inter) and len(inter) == len(mat_nms[j]):
                    if len(inter) / float(len(i.data["names"])) > cluster_prop and len(inter) > smallest_cluster:
                        print i.label,clusterind[j],len(inter),len(i.data["names"])
                        keepers.add(clusterind[j].replace(".fa",".aln"))
        else:
            for j in clusterind:
                inter = set(i.data["names"]).intersection(set(mat_nms[j]))
                keep = False
                if len(i.data["names"]) > 100:
                    if len(inter)/float(len(i.data["names"])) > cluster_prop:
                        print clusterind[j],len(inter),len(i.data["names"])
                        keep = True
                else:
                    if len(inter)/float(len(i.data["names"])) > cluster_prop+0.5:
                        print clusterind[j],len(inter),len(i.data["names"])
                        keep = True
                if keep == True:
                    keepers.add(clusterind[j].replace(".fa",".aln"))
    return

def make_trim_trees(alignments):
    if check_for_programs.which_program("FastTree") == None:
        print colored.red("FastTree NOT IN PATH"),colored.red(emoticons.get_ran_emot("sad"))
        sys.exit(1)
    newalns = {}
    for i in alignments:
        print "making tree for",i
        cmd = "FastTree -nt -gtr "+i+" > "+i.replace(".aln",".tre")+" 2> /dev/null"
        os.system(cmd)
        cmd = "python "+DI+"trim_tips.py "+i.replace(".aln",".tre")+" "+str(relcut)+" "+str(abscut)
        #print cmd
        p = subprocess.Popen(cmd, shell=True,stderr = subprocess.PIPE,stdout = subprocess.PIPE)
        outtre = p.stdout.read().strip()
        outrem = p.stderr.read().strip()
        if len(outrem) > 0:
            print "  removing",len(outrem.split("\n")),"tips"
            removetax = []
            for j in outrem.split("\n"):
                taxon = j.split(" ")[1]
                removetax.append(taxon)
            cmd = "pxrms -s "+i+" -n "+",".join(removetax)+" -o "+i.replace(".aln",".aln.ed")
            newalns[i] = i.replace(".aln",".aln.ed")
            #print cmd
            os.system(cmd)
    return newalns

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "python "+sys.argv[0]+" startdir"
        sys.exit(0)

    cld = sys.argv[1]
    #take off the trailing slash if there is one
    if cld[-1] == "/":
        cld = cld[0:-1]

    count = 0
    tree = node.Node()
    nodes = {}
    firstnode = True
    
    #build a tree from the directory
    for root, dirs, files in os.walk(cld, topdown = True):
        if "clusters" in root:
            continue
        if "clusters" in dirs:
            if firstnode == True:
                tree.label = root.split("/")[-1]
                firstnode = False
                nodes[root.split("/")[-1]] = tree
            nd = nodes[root.split("/")[-1]]
            nd.data["dir"] = root
            nd.data["names"] = set()
            tf = open(root+"/"+root.split("/")[-1]+".table","r")
            for i in tf:
                spls = i.strip().split("\t")
                nd.data["names"].add(spls[4])
            tf.close()
            for j in dirs:
                if "clusters" not in j:
                    cnd = node.Node()
                    cnd.label = j
                    cnd.parent = nd
                    nd.add_child(cnd)
                    nodes[j] = cnd
            count += 1

    record_info_table(cld+"/info.csv")

    check_info_table(tree)
    print len(keepers)


    # do you want to rename these ones?
    rename = raw_input("Do you want to rename these clusters? y/n/# ")
    if rename == 'y' or rename == '#':
        keeps = None
        if rename == '#':
            nums = raw_input("List cluster numbers separated by spaces: ")
            keeps = [cld+"/clusters/cluster"+i+".aln" for i in nums.split(" ")]
        else:
            keeps = [cld+"/clusters/"+i for i in keepers]
        # do you want to make trees and trim tips?
        maketrees = raw_input("Do you want to make trees and trim tips for these gene regions? y/n ")
        if maketrees == 'y':
            newalns = make_trim_trees(keeps)
            if len(newalns) > 0:
                for i in newalns:
                    keeps.remove(i)
                    keeps.append(newalns[i])
        tab = cld+"/"+cld.split("/")[-1]+".table"
        rtn = cld.split("/")[-1]
        cmd = "python "+DI+"change_id_to_ncbi_fasta_mult.py "+tab+" "+ " ".join(keeps)
        #print cmd
        os.system(cmd)
        concat = raw_input("Do you want to concat? y/n ")
        if concat == 'y':
            cmd = "pxcat -s "+" ".join([i+".rn" for i in keeps])+" -o "+cld+"/"+rtn+"_outaln -p "+cld+"/"+rtn+"_outpart"
            #print cmd
            os.system(cmd)
        constraint = raw_input("Do you want to make a constraint? y/n ")
        if constraint == 'y':
            dbname = raw_input("Where is the DB? ")
            #baseid = raw_input("What is the baseid? ")
            baseid = cld.split("_")[-1]
            if len(dbname) > 2 and len(baseid) > 2:
                cmd = "python "+DI+"make_constraint_from_ncbialn.py "+dbname+" "+baseid+" "+cld+"/"+rtn+"_outaln > "+cld+"/"+rtn+"_outaln.constraint.tre"
                os.system(cmd)
            print "line for get_min"
            print "python "+DI+"get_min_overlap_multiple_seqs.py "+cld+"/"+rtn+"_outaln.constraint.tre "+" ".join([i+".rn" for i in keeps])

