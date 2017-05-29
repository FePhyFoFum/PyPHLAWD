import sys
import os
import tree_reader
import tree_utils
import node

VERBOSE = True
EXTRACT = False#True# alternative is that it will insert into the big tree instead of return the root
ADDMISSING = True

def get_nds_names(nms,tre):
    nds = []
    for i in tre.leaves():
        if i.label in nms:
            nds.append(i)
    return nds

def remove_int_ext_nodes(nms,tre):
    toremove = []
    for i in tre.iternodes():
        if len(i.children) > 0:
            if i.label in nms:
                toremove.append(i)
    for i in toremove:
        sys.stderr.write("remove internal: "+i.get_newick_repr(False)+"\n")
        par = i.parent
        par.remove_child(i)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "python "+sys.argv[0]+ " addtree bigtre"
        sys.exit(0)

    tree1 = tree_reader.read_tree_file_iter(sys.argv[1]).next()
    tree_utils.set_heights(tree1)
    bigtree = tree_reader.read_tree_file_iter(sys.argv[2]).next()
    tree_utils.set_heights(bigtree)

    rootnms = set(tree1.lvsnms())
    
    remove_int_ext_nodes(rootnms,bigtree)

    othernms = set(bigtree.lvsnms())
    if VERBOSE:
        ddifs = rootnms.difference(othernms)
        for i in ddifs:
            sys.stderr.write(i+"\n")
    diffnms = []
    diffnds = {}
    didit = False
    nrt = tree_utils.get_mrca_wnms(list(rootnms.intersection(othernms)),bigtree).parent

    try:
        sys.stderr.write("new root label:"+nrt.label+"\n")
    except:
        sys.stderr.write("new root label:") 

    rm = []
    for i in nrt.children:
        if VERBOSE:
            sys.stderr.write(str(len(i.lvsnms()))+" "+str(len(rootnms))+"\n")
        xs = set(i.lvsnms()).intersection(rootnms)
        if len(xs)>0:
            rm.append(i)
            if ADDMISSING:
                xd = set(i.lvsnms()).difference(rootnms)
                for j in xd:
                    diffnms.append(j)
                    diffnds[j] = i.get_leaf_by_name(j)
    for i in rm:
        nrt.remove_child(i)
    #if VERBOSE:
    #    sys.stderr.write(nrt.get_newick_repr(True)+"\n")
    testlength = nrt.height-tree1.height
    if testlength < 0:
        tree_utils.scale_edges(tree1,nrt.height-1)
        tree1.length = 1
    else:
        tree1.length = testlength
    nrt.add_child(tree1)
    tree1.label = sys.argv[1].split("/")[-1]
    if ADDMISSING:
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
                        #    sys.stderr.write("add at this node"+" "+par.get_newick_repr(False)+" "+amrca.get_newick_repr(False)+"\n")
                        if len(pln) == 1:
                            amrca = tree1.get_leaf_by_name(list(pln)[0])
                            #print "f",amrca.get_newick_repr(True)
                            nn = node.Node()
                            nn.length = amrca.length/2.
                            nn.height = amrca.height+amrca.length/2.
                            amrca.length = nn.length
                            amrca.parent.add_child(nn)
                            amrca.parent.remove_child(amrca)
                            nn.add_child(amrca)
                            amrca = nn
                        for k in par.children:
                            if len(set(k.lvsnms()).intersection(rootnms)) > 0:
                                continue
                            else:
                                #tree_utils.set_heights(amrca)
                                #print "a",k.get_newick_repr(True),amrca.length,amrca.get_newick_repr(True),amrca.height
                                if len(k.leaves()) > 1 or len(k.children) > 0:
                                    tree_utils.scale_edges(k,amrca.height)
                                else:
                                    #print "b",k.get_newick_repr(True),amrca.height
                                    k.length = amrca.height
                                #print "c",k.get_newick_repr(True)
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

