import sys
import tree_reader
import tree_utils
import seq

"""
this will read the file created from run_post_constraint_test.py
and remove the constraint from the constraint tree and remove the 
taxa from the tree and the alignment

if you give the previous tree it will do another procedure where
it will leave the rest of the tree but move the other taxa to the
parent. tree needs to be rooted
"""

if __name__ == "__main__":
    if len(sys.argv) != 4 and len(sys.argv) != 5:
        print "python "+sys.argv[0]+" toremove constrainttre aln [MLTREE.rooted]"
        sys.exit(0)

    removetaxa = set()
    remove_mrca = []

    tr = open(sys.argv[1],"r")
    for i in tr:
        spls = i.strip().split(":")
        if "taxon" in spls[0]:
            removetaxa.add(spls[1])
        elif "constraint" in spls[0]:
            remove_mrca.append(spls[1].split(","))
    tr.close()

    tr = open(sys.argv[3]+".postrem","w")
    for i in seq.read_fasta_file_iter(sys.argv[3]):
        if i.name not in removetaxa:
            tr.write(i.get_fasta())
    tr.close()

    tree = tree_reader.read_tree_file_iter(sys.argv[2]).next()
    nodes = {}
    mrca_pars = [] #vector of the parents of each remove constraint
    child_constraints = [] #vector of child_constraints for each remove constraint
    for i in tree.leaves():
        nodes[i.label] = i
    for i in remove_mrca:
        tnods = []
        for j in i:
            tnods.append(nodes[j])
        mr = tree_utils.get_mrca(tnods,tree)
        par = mr.parent
        tchild_constraints = []
        for j in  mr.children:
            if len(j.children) > 0:
                tchild_constraints.append(j)
            j.parent = par
            par.add_child(j)
        child_constraints.append(tchild_constraints)
        par.remove_child(mr)
        mrca_pars.append(par)
    for i in removetaxa:
        par = nodes[i].parent
        par.remove_child(nodes[i])
        if len(par.children) == 1:
            pp = par.parent
            pp.add_child(par.children[0])
            pp.remove_child(par)
    tr = open(sys.argv[2]+".postrem","w")
    tr.write(tree.get_newick_repr(False)+";")
    tr.close()

    if len(sys.argv) == 5:
        mtree = tree_reader.read_tree_file_iter(sys.argv[4]).next()
        mnodes = {}
        for i in mtree.leaves():
            mnodes[i.label] = i
        for i in range(len(remove_mrca)):
            #first get the node on the constraint tree
            mtnods = []
            mr = None
            for j in remove_mrca[i]:
                # just removeing from the ML, if you uncomment below, you need to uncomment this
                removetaxa.add(j)
                #mtnods.append(mnodes[j])
                #mr = tree_utils.get_mrca(mtnods,mtree)
            """
            connect = None
            mtnods = []
            for j in mrca_pars[i].lvsnms():
                mtnods.append(mnodes[j])
                connect = tree_utils.get_mrca(mtnods,mtree)
            notdone = set(mr.lvsnms())
            for j in child_constraints[i]:
                mtnods = []
                for k in j:
                    mtnods.append(mnodes[k])
                    mr2 = tree_utils.get_mrca(mtnods,mtree)
                par = mr2.parent
                par.remove_child(mr2)
                connect.add_child(mr2)
                mr2.parent = connect
                notdone = notdone.difference(mr.lvsnms())
            for j in notdone:
                mnodes[j].parent = connect
                connect.add_child(mnodes[j])
            parmr = mr.parent
            parmr.remove_child(mr)
            if len(parmr.children) == 1:
                och = parmr.children[0]
                pparmr = parmr.parent
                pparmr.remove_child(parmr)
                pparmr.add_child(och)
            """
        for i in removetaxa:
            par = mnodes[i].parent
            par.remove_child(mnodes[i])
            if len(par.children) == 1:
                pp = par.parent
                pp.add_child(par.children[0])
                pp.remove_child(par)
        tr = open(sys.argv[4]+".postrem","w")
        tr.write(mtree.get_newick_repr(False)+";")
        tr.close()


                
