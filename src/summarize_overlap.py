import sys
import tree_reader
import seq

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "python "+sys.argv[0]+" aln tre"
        sys.exit(0)
    seqs = seq.read_fasta_file(sys.argv[1])
    tre = tree_reader.read_tree_file_iter(sys.argv[2]).next()
    seqsd = {}
    for i in seqs:
        x = i.seq.lower().replace("a","1").replace("c","1").replace("g","1").replace("t","1")
        seqsd[i.name] = set([j for j,ltr in enumerate(x) if ltr == "1"])
    for i in tre.leaves():
        i.data["s"] = seqsd[i.label]
    seqsd = None
    for i in tre.iternodes(order="postorder"):
        if len(i.children) == 0:
            i.data["c"] = {}
            for j in i.data["s"]:
                i.data["c"][j] = 1
            continue
        if i == tre:
            continue
        lfs = set()
        x = i.children[0].data["s"]
        y = i.children[1].data["s"]
        i.data["i"] = len(x.intersection(y))
        i.data["s"] = x.union(y)
        i.label = str(i.data["i"])+".1"
    print tre.get_newick_repr(True)+";"
