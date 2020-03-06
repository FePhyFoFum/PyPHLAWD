import sys
import os
import shlex
import subprocess
import check_for_programs
from conf import DI
from conf import relcut
from conf import abscut
from conf import abscutint
from conf import usecython
from conf import smallest_cluster
from conf import cluster_prop
from conf import py
import emoticons
from clint.textui import colored
if usecython:
    import cnode as node
else:
    import node
import argparse as ap

"""
same as find_good_clusters_for_concat.py, except automated.
- accepts default clusters, builds trees and trims tips, concatenates, renames
"""


"""
this assumes that you have already run 
post_process_cluster_info.py startdir
"""

mat_nms = []
clusterind = {}
keepers = set()#node

def generate_argparser():
    parser = ap.ArgumentParser(prog="find_good_clusters_for_concat_batch.py",
        formatter_class=ap.ArgumentDefaultsHelpFormatter)
    parser = ap.ArgumentParser()
    parser.add_argument("-d", "--dir", type=str, required=True,
        help=("Starting directory."))
    parser.add_argument("-b","--database",type=str,required=True,
        help=("Database with sequences."))
    parser.add_argument("-i", "--includetrivial", action="store_true", required=False,
        default=False, help=("Include trivial clusters (default = False)"))
    return parser

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

# where default clusters are selected
# picked by coverage (conditioned on minimum size of 3 (rooted) or 4 (unrooted)) and smallest size defined
# if trivial is True, and=y cluster > cluster_prop is retained
def check_info_table(tree, trivial):
    for i in tree.iternodes(order="POSTORDER"):
        if "names" not in i.data:
            continue
        if i.parent != None:
            for j in clusterind:
                inter = set(i.data["names"]).intersection(set(mat_nms[j]))
                pinter = set(i.parent.data["names"]).intersection(set(mat_nms[j]))
                if len(inter) > 0 and len(pinter) == len(inter) and len(inter) == len(mat_nms[j]):
                    # whether the `and` below should be `or` (like for the root).
                    if len(inter) / float(len(i.data["names"])) > cluster_prop or len(inter) > smallest_cluster:
                        if not trivial:
                            if (len(inter) > 3):
                                print(i.label,clusterind[j],len(inter),len(i.data["names"]))
                                keepers.add(clusterind[j].replace(".fa",".aln"))
                        else:
                            print(i.label,clusterind[j],len(inter),len(i.data["names"]))
                            keepers.add(clusterind[j].replace(".fa",".aln"))
        else:
            for j in clusterind: # root
                inter = set(i.data["names"]).intersection(set(mat_nms[j]))
                if len(inter)/float(len(i.data["names"])) > cluster_prop or len(inter) > smallest_cluster:
                    if not trivial: # default: require a phylogenetically minimum size of at least 4
                        if (len(inter) > 3):
                            print(clusterind[j],len(inter),len(i.data["names"]))
                            keepers.add(clusterind[j].replace(".fa",".aln"))
                    else:
                        print(clusterind[j],len(inter),len(i.data["names"]))
                        keepers.add(clusterind[j].replace(".fa",".aln"))
                        
    return

def make_trim_trees(alignments):
    fasttreename = "FastTree"
    if check_for_programs.which_program("FastTree") == None:
        if check_for_programs.which_program("fasttree") != None:
            fasttreename = "fasttree"
        else:
            print(colored.red("FastTree NOT IN PATH"),colored.red(emoticons.get_ran_emot("sad")))
            sys.exit(1)
    newalns = {}
    for i in alignments:
        print("making tree for",i)
        cmd = fasttreename+" -nt -gtr "+i+" > "+i.replace(".aln",".tre")+" 2> /dev/null"
        os.system(cmd)
        cmd = py+" "+DI+"trim_tips.py "+i.replace(".aln",".tre")+" "+str(relcut)+" "+str(abscut)
        #print cmd
        p = subprocess.Popen(cmd, shell=True,stderr = subprocess.PIPE,stdout = subprocess.PIPE)
        outtre = p.stdout.read().strip()
        outrem = p.stderr.read().strip()
        removetax = set()
        if len(outrem) > 0:
            outrem = outrem.decode("utf-8")
            print("  removing",len(str(outrem).split("\n")),"tips")
            for j in str(outrem).split("\n"):
                taxon = j.split(" ")[1]
                removetax.add(taxon)
        cmd = py+" "+DI+"trim_internal_edges.py "+i.replace(".aln",".tre")+" "+str(abscutint)
        #print cmd
        p = subprocess.Popen(cmd, shell=True,stderr = subprocess.PIPE,stdout = subprocess.PIPE)
        outtre = p.stdout.read().strip()
        outrem = p.stderr.read().strip()
        if len(outrem) > 0:
            outrem = outrem.decode("utf-8")
            print("  removing",len(str(outrem).split("\n")),"tips")
            for j in str(outrem).split("\n"):
                taxon = j.split(" ")[1]
                removetax.add(taxon)
        if len(removetax) > 0:
            cmd = "pxrms -s "+i+" -n "+",".join(list(removetax))+" -o "+i.replace(".aln",".aln.ed")
            newalns[i] = i.replace(".aln",".aln.ed")
            #print cmd
            os.system(cmd)
        
    return newalns

if __name__ == "__main__":
    parser = generate_argparser()
    if len(sys.argv[1:]) == 0:
        sys.argv.append("-h")
    args = parser.parse_args(sys.argv[1:])
    dbname = args.database
    cld = args.dir
    #take off the trailing slash if there is one
    if cld[-1] == "/":
        cld = cld[0:-1]
    
    trivial = args.includetrivial
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
    #print(tree.get_newick_repr()+";")
    check_info_table(tree, trivial)
    print(len(keepers))
    
    ## hard-coded stuff: rename default selected clusters, make trees, concat, constraint
    # baseid
    baseid = cld.split("_")[-1]
    # clusters to keep
    keeps = [cld+"/clusters/"+i for i in keepers]
    # make trees and trim tips
    newalns = make_trim_trees(keeps)
    if len(newalns) > 0:
        for i in newalns:
            keeps.remove(i)
            keeps.append(newalns[i])
    # table
    tab = cld+"/"+cld.split("/")[-1]+".table"
    rtn = cld.split("/")[-1]
    # change ids to NCBIids
    cmd = py+" "+DI+"change_id_to_ncbi_fasta_mult.py "+tab+" "+ " ".join(keeps)
    os.system(cmd)
    # concatenate and switch to uppercase
    outaln = cld+"/"+rtn+"_outaln"
    cmd = "pxcat -u -s "+" ".join([i+".rn" for i in keeps])+" -o "+outaln+" -p "+cld+"/"+rtn+"_outpart"
    os.system(cmd)
    # make constraint tree
    ctree = cld+"/"+rtn+"_outaln.constraint.tre"
    cmd = py+" "+DI+"make_constraint_from_ncbialn.py "+dbname+" "+baseid+" "+outaln+" > "+ctree
    print("make constraint tree:")
    print(cmd)
    os.system(cmd)
    
    # rename NCBIids to names
    # tree
    cmd = py+" "+DI+"change_ncbi_to_name_tre.py -t "+tab+" -i "+ctree+" -o "+cld+"/"+rtn+"_outaln.constraint.cn.tre"
    print("rename taxa in tree:")
    print(cmd)
    os.system(cmd)
    # seqs
    cmd = py+" "+DI+"change_ncbi_to_name_fasta.py -t "+tab+" -i "+outaln+" -o "+outaln+"_renamed"
    print("rename taxa in concatenated alignment:")
    print(cmd)
    os.system(cmd)

    print("line for get_min:")
    print("python3 "+DI+"get_min_overlap_multiple_seqs.py "+cld+"/"+rtn+"_outaln.constraint.tre "+" ".join([i+".rn" for i in keeps]))
    