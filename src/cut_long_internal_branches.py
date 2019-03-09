"""
Cut long internal branches
If no long branch, copy the input tree to the out dir for the next round

The input trees can be .tre, .tre.mm or .tre.mm.tt depends on the workflow
"""

import tree_reader,os,sys,math
import conf
if conf.usecython:
    import cnode as node
else:
    import node
from tree_utils import get_front_names,remove_kink,get_front_labels
from shutil import copy
from logger import Logger

def cut_long_internal_branches(curroot,cutoff,min_taxa):
    """cut long branches and output all subtrees with at least 4 tips"""
    going = True
    subtrees = [] #store all subtrees after cutting
    while going:
        going = False #only keep going if long branches were found during last round
        for node in curroot.iternodes(): #Walk through nodes
            if node.istip or node == curroot: continue
            child0,child1 = node.children[0],node.children[1]
            if node.length > cutoff:
                print(node.length)
                if not child0.istip and not child1.istip and child0.length+child1.length>cutoff:
                    print(child0.length + child1.length)
                    if len(child0.leaves()) >= min_taxa:
                        subtrees.append(child0)
                    if len(child1.leaves()) >= min_taxa:
                        subtrees.append(child1)                        
                else: subtrees.append(node)
                node = node.prune()
                if len(curroot.leaves()) > 2: #no kink if only two left
                    node,curroot = remove_kink(node,curroot)
                    going = True
                break
    if len(curroot.leaves()) >= min_taxa:
        subtrees.append(curroot) #write out the residue after cutting
    return subtrees

def main(inDIR,file_ending,branch_len_cutoff,min_taxa,outDIR,log):
    """cut long branches and output subtrees as .subtre files
    if uncut and nothing changed betwee .tre and .subtree
    copy the original .tre file to the outdir"""
    if inDIR[-1] != "/": inDIR += "/"
    min_taxa = int(min_taxa)
    filecount = 0
    cutoff = float(branch_len_cutoff)
    print("cutting branches longer than",cutoff)
    for i in os.listdir(inDIR):
        if not i.endswith(file_ending): continue
        #print i
        filecount += 1
        with open(inDIR+i,"r") as infile: #only 1 tree in each file
            intree = tree_reader.read_tree_string(infile.readline())
        try:
            with open(inDIR+i[:i.find(".tre")]+".tre","r") as infile: #the original .tre
                raw_tree_size = len(get_front_labels(tree_reader.read_tree_string(infile.readline())))
        except: # did not refine this round. Use the .tre.tt.mm tree
            raw_tree_size = len(get_front_labels(intree))
        num_taxa = len(intree.leaves())
        if num_taxa < min_taxa:
            print("Tree has",num_taxa,"less than", min_taxa,"taxa")
        else:
            #print ".tre:",raw_tree_size,"tips; "+file_ending+": "+str(len(get_front_labels(intree)))+" tips"
            subtrees = cut_long_internal_branches(intree,cutoff,min_taxa)
            if len(subtrees) == 0:
                print("No tree with at least", min_taxa, "taxa")
            else:
                count = 0
                outsizes = ""
                for subtree in subtrees:
                    if len(subtree.leaves()) >= min_taxa:
                        if len(subtree.children) == 2: #fix bifurcating roots from cutting
                            temp,subtree = remove_kink(subtree,subtree)
                        count += 1
                        outname = outDIR+"/"+i.split(".")[0]+"_"+str(count)+".subtree"
                        print(outname)
                        with open(outname,"w") as outfile:
                            outfile.write(subtree.get_newick_repr(True)+";\n")
                        outsizes += str(len(subtree.leaves()))+", "
                print(count,"tree(s) written. Sizes:",outsizes)
            
        
if __name__ == "__main__":
    if len(sys.argv) != 6 and len(sys.argv) != 7:
        print("python cut_long_internal_branches.py inDIR tree_file_ending internal_branch_length_cutoff minimal_taxa outDIR [logfile]")
        sys.exit(0)
    LOGFILE = "pyphlawd.log"
    if len(sys.argv) == 7:
        LOGFILE = sys.argv[6]
        sys.argv=sys.argv[1:-1]
    else:
        sys.argv=sys.argv[1:]
    log = Logger(LOGFILE)
    inDIR,file_ending,branch_len_cutoff,min_taxa,outDIR = sys.argv
    main(inDIR,file_ending,branch_len_cutoff,min_taxa,outDIR,log)

        
