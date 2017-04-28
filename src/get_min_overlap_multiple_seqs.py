import sys
import os
import seq
import networkx as nx
import tree_reader
from networkx.drawing.nx_agraph import write_dot


"""
This will make a graph of the connectivity of the genes and taxa
given some tree (probably taxonomy) and a set of genes
"""

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print "python "+sys.argv[0]+" tree files..."
        sys.exit(0)
    
    tree = tree_reader.read_tree_file_iter(sys.argv[1]).next()
    genes = {}
    seqfiles = []
    badseqs = []
    goodseqs = []
    for i in sys.argv[2:]:
        if i[0] != "_":
            seqfiles.append(i)
        else:
            goodseqs.append(i[1:])
    for i in seqfiles:
        genes[i] = []
        for j in seq.read_fasta_file_iter(i):
            genes[i].append(j.name)

    print seqfiles
    print goodseqs
    filt = set()

    for i in tree.iternodes(order="POSTORDER"):
        if len(i.children) == 0:
            continue
        lvsnms = i.lvsnms()
        lvsnmsin = set()
        G = nx.MultiGraph()
        gene_per_taxon = {}
        for j in genes:
            ndgenes = []
            for k in genes[j]:
                if k not in lvsnms:
                    continue
                if k not in G:
                    G.add_node(k)
                    gene_per_taxon[k] = []
                lvsnmsin.add(k)
                gene_per_taxon[k].append(j)
                for l in ndgenes:
                    G.add_edge(k,l,gene=j)
                ndgenes.append(k)
        
        for j in gene_per_taxon:
            if len(gene_per_taxon[j]) == 1:
                if gene_per_taxon[j][0] not in goodseqs:
                    G.remove_node(j)
                    filt.add(j)

        x = list(nx.connected_components(G))
        if len(x) > 1:
            largest = 0
            largestin = None
            for j in range(len(x)):
                if len(G.edges(x[j])) > largest:
                    largest = len(G.edges(x[j]))
                    largestin = j
            for j in range(len(x)):
                if j != largestin:
                    for k in x[j]:
                        filt.add(k)
            print x,len(lvsnmsin)
    
    if len(filt) > 0:
        alnfile = raw_input("Concat aln filename: ")
        treefile = sys.argv[1]
        if len(alnfile) > 2 and len(treefile) > 2:
            cmd = "pxrmt -t "+treefile+" -n "+",".join(list(filt))+" > "+treefile+".filt"
            print cmd
            os.system(cmd)
            cmd = "pxrms -s "+alnfile+" -n "+",".join(list(filt))+" > "+alnfile+".filt"
            print cmd
            os.system(cmd)
