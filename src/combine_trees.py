import sys
import os
import tree_reader
import tree_utils
import node

VERBOSE = True
EXTRACT = True # alternative is that it will insert into the big tree instead of return the root

"""
this is a proof of concept to get trees combined
one needs to be preferred over another
"""

def get_nds_names(nms,tre):
    nds = []
    for i in tre.leaves():
        if i.label in nms:
            nds.append(i)
    return nds


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "python "+sys.argv[0]+ " addtree bigtre"
        sys.exit(0)

    tree1 = tree_reader.read_tree_file_iter(sys.argv[1]).next()
    bigtree = tree_reader.read_tree_file_iter(sys.argv[2]).next()

    rootnms = set(tree1.lvsnms())
    othernms = set(bigtree.lvsnms())
    if VERBOSE:
        ddifs = rootnms.difference(othernms)
        for i in ddifs:
            sys.stderr.write(i+"\n")
    diffnms = []
    diffnds = {}
    didit = False
    nrt = tree_utils.get_mrca_wnms(list(rootnms.intersection(othernms)),bigtree).parent
    sys.stderr.write("new root label:"+nrt.label+"\n")
    rm = []
    for i in nrt.children:
        if VERBOSE:
            sys.stderr.write(str(len(i.lvsnms()))+" "+str(len(rootnms))+"\n")
        xs = set(i.lvsnms()).intersection(rootnms)
        if len(xs)>0:
            rm.append(i)
            xd = set(i.lvsnms()).difference(rootnms)
            for j in xd:
                diffnms.append(j)
                diffnds[j] = i.get_leaf_by_name(j)
    for i in rm:
        nrt.remove_child(i)
    #if VERBOSE:
    #    sys.stderr.write(nrt.get_newick_repr(False)+"\n")
    nrt.add_child(tree1)
    if VERBOSE:
        sys.stderr.write("here\n")
    while len(diffnms) > 0:
        for j in diffnms:
            going = True
            cn = diffnds[j]
            while going:
                par = cn.parent
                pln = set(par.lvsnms()).intersection(rootnms)
                if len(pln) > 0:
                    amrca = tree_utils.get_mrca_wnms(pln,tree1)
                    #if VERBOSE:
                        #sys.stderr.write("add at this node"+" "+par.get_newick_repr(False)+" "+amrca.get_newick_repr(False)+"\n")
                    if len(pln) == 1:
                        amrca = tree1.get_leaf_by_name(list(pln)[0])
                        nn = node.Node()
                        nn.length = amrca.length
                        amrca.length = 0.0
                        amrca.parent.add_child(nn)
                        amrca.parent.remove_child(amrca)
                        nn.add_child(amrca)
                        amrca = nn
                    for k in par.children:
                        if len(set(k.lvsnms()).intersection(rootnms)) > 0:
                            continue
                        else:
                            amrca.add_child(k)
                            for m in k.lvsnms():
                                diffnms.remove(m)
                    going = False
                cn = par
        break

    if EXTRACT:
        print tree1.get_newick_repr(True)+";"
    else:
        print bigtree.get_newick_repr(True)+";"

