"""
Trim tips that sticking out (> relative_cutoff and >10 times longer than sister)
Also trim any tips that are > absolute_cutoff
"""
import os
import sys
import node
import tree_reader
from tree_utils import *

#how much larger does the sister have to be
timesabove = 6

def errwrite(tx):
    sys.stderr.write(tx+"\n")

#return the outlier tip, with abnormal high contrast and long branch
def check_countrast_outlier(node0,node1,above0,above1,relative_cutoff):
    if node0.istip and above0>relative_cutoff:
        if above1 == 0.0 or above0/above1 > timesabove:
            return node0
    if node1.istip and above1>relative_cutoff:
        if above0 == 0.0 or above1/above0 > timesabove:
            return node1
    return None
    
def remove_a_tip(root,tip_node):
    errwrite("removing: "+tip_node.label+" "+str(tip_node.length))
    node = tip_node.prune()
    if len(root.leaves()) > 3:
        node,root = remove_kink(node,root)
        return root
    else:
        return None
    
def trim(curroot,relative_cutoff,absolute_cutoff):
    removed = []
    #if len(curroot.children) == 2:
    #    temp,root = remove_kink(curroot,curroot)
    going = True
    while going and len(curroot.leaves()) > 3:
        going = False
        for i in curroot.iternodes(order="POSTORDER"):# POSTORDER
            if len(i.children) == 0: # at the tip
                i.data['len'] = i.length
                if i.length > absolute_cutoff:
                    curroot = remove_a_tip(curroot,i)
                    removed.append(i.label)
                    going = True
                    break
            elif len(i.children) == 1: # kink in tree
                remove_kink(i,curroot)
                going = True
                break
            elif len(i.children) == 2: # normal bifurcating internal nodes
                child0,child1 = i.children[0],i.children[1]
                above0,above1 = child0.data['len'],child1.data['len']
                i.data['len'] = ((above0+above1)/2.)+i.length #stepwise average
                outlier = check_countrast_outlier(child0,child1,above0,above1,relative_cutoff)
                if outlier != None:
                    curroot = remove_a_tip(curroot,outlier)
                    removed.append(outlier.label)
                    going = True #need to keep checking
                    break
            else: #3 or more branches from this node. Pair-wise comparison
                total_len = 0
                nchild = len(i.children)
                for child in i.children:
                    total_len += child.data['len']
                i.data['len'] = total_len / float(len(i.children))
                keep_checking = True
                for index1 in range(nchild): #do all the pairwise comparison
                    for index2 in range(nchild):
                        if index2 <= index1:
                            continue #avoid repeatedly checking a pair
                        child1,child2 = i.children[index1],i.children[index2]
                        above1,above2 = child1.data['len'], child2.data['len']
                        outlier = check_countrast_outlier(child1,child2,above1,above2,relative_cutoff)
                        if outlier != None:
                            curroot = remove_a_tip(curroot,outlier)
                            removed.append(outlier.label)
                            going = True #need to keep checking
                            keep_checking = False #to break the nested loop
                            break
                    if not keep_checking: break
    return curroot,removed
    
def main(treefile,relative_cut,absolute_cut):
    intree = None
    with open(treefile,"r") as infile:
        intree = tree_reader.read_tree_string(infile.readline())
    outtree,removed = trim(intree,float(relative_cut),float(absolute_cut))
    print(outtree.get_newick_repr(True)+";")
    return outtree,removed

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("python "+sys.argv[0]+" file.tre relative_cutoff absolute_cutoff")
        sys.exit(0)

    treefile = sys.argv[1]
    rel_cut = sys.argv[2]
    abs_cut = sys.argv[3]
    main(treefile,rel_cut,abs_cut)

    
