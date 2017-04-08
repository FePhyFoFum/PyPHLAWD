import sys
import tree_reader
import tree_utils
import seq

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print "python "+sys.argv[0]+" toremove constrainttre aln"
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
    for i in tree.leaves():
        nodes[i.label] = i
    for i in remove_mrca:
        tnods = []
        for j in i:
            tnods.append(nodes[j])
        mr = tree_utils.get_mrca(tnods,tree)
        par = mr.parent
        for j in  mr.children:
            j.parent = par
            par.add_child(j)
        par.remove_child(mr)
    for i in removetaxa:
        print i
        par = nodes[i].parent
        par.remove_child(nodes[i])
        if len(par.children) == 1:
            pp = par.parent
            pp.add_child(par.children[0])
            pp.remove_child(par)
            print pp.get_newick_repr(False)
        else:
            print par.get_newick_repr(False)
    tr = open(sys.argv[2]+".postrem","w")
    tr.write(tree.get_newick_repr(False)+";")
    tr.close()

