import os
import sys
from tree_reader import *
from conf import DI
import operator

badfreq = 0.45
smallcut = 0.1

"""
this will write a constraint_processing_file that will need to be
examined after a constraint is made and it will remove the relevant nodes
and then it will remove the taxa from the alignments
"""

def process_first_result(fl):
    f = open(fl,"r")
    f.readline()
    x = f.readline().strip()
    spls = x.split(",")
    f.close()
    return float(spls[1])

def process_second_result(fl):
    f = open(fl,"r")
    f.readline()
    nms = {}
    for i in f:
        spls = i.strip().split(",")
        nms[spls[0]] = float(spls[3])
    f.close()
    sorted_x = sorted(nms.items(), key=operator.itemgetter(1))
    below01 = []
    for i in sorted_x:
        if i[1] < smallcut:
            below01.append(i[0])
    mincut = max(len(nms)*.05,3)
    if len(below01) < mincut:
        return below01
    else:
        return None


if __name__ == "__main__":
    if len(sys.argv) != 6:
        print "python "+sys.argv[0]+" constrainttre calculatedtree alnfile partfile outfile"
        sys.exit(0)
    tree = read_tree_file_iter(sys.argv[1]).next()
    treefile = sys.argv[2]
    alnfile = sys.argv[3]
    partfile = sys.argv[4]
    lose = set()
    remove_taxa = set()
    for i in tree.iternodes():
        if len(i.children) == 0 or i == tree:
            continue
        else:
            nms = i.lvsnms()
            cmd = "python "+DI+"/quartet_sampling.py -t "+treefile+" -n "+alnfile+" -# 300 -T 4 -q "+partfile+" -C "+",".join(nms)+" -P > /dev/null 2>&1"
            os.system(cmd)
            firstres = process_first_result("RESULT.node_scores.csv")
            if firstres < badfreq:
                print "lose constraint"
                if i.label == "":
                    print firstres,",".join(nms)
                else:
                    print firstres,i.label
                cmd = "python "+DI+"/quartet_sampling.py -t "+treefile+" -n "+alnfile+" -# 500 -T 4 -q "+partfile+" -C "+",".join(nms)+" -P -m > /dev/null 2>&1"
                os.system(cmd)
                secondres = process_second_result("RESULT.node_scores.csv.clade")
                if secondres != None:
                    print "would remove ",secondres
                    for j in secondres:
                        remove_taxa.add(j)
                else:
                    lose.add(i)
    outfile = open(sys.argv[5],"w")
    for i in remove_taxa:
        outfile.write("remove_taxon:"+i+"\n")
    for i in lose:
        outfile.write("remove_constraint:"+",".join(i.lvsnms())+"\n")
    outfile.close()
