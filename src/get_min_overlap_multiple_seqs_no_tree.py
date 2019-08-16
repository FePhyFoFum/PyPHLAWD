import sys
import os
import seq
import networkx as nx
from networkx.drawing.nx_agraph import write_dot


"""
This will make a graph of the connectivity of the genes and taxa
given some tree (probably taxonomy) and a set of genes
"""

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("python "+sys.argv[0]+" files...")
        sys.exit(0)
    
    genes = {}
    seqfiles = []
    badseqs = []
    goodseqs = []
    allnames = set()
    for i in sys.argv[1:]:
        if i[0] != "_":
            seqfiles.append(i)
        else:
            goodseqs.append(i[1:])
    for i in seqfiles:
        genes[i] = []
        for j in seq.read_fasta_file_iter(i):
            genes[i].append(j.name)
            allnames.add(j.name)

    print(seqfiles)
    print(goodseqs)
    filt = set()


    lvsnms = list(allnames)
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
    """import matplotlib.pyplot as plt
    nx.draw(G)
    print(G)
    plt.show()
    """
    """
    for j in gene_per_taxon:
        if len(gene_per_taxon[j]) == 1:
            if gene_per_taxon[j][0] not in goodseqs:
                G.remove_node(j)
                filt.add(j)
    """
    
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
        print(x,len(lvsnmsin))
    
    if len(filt) > 0:
        alnfile = input("Concat aln filename: ")
        if len(alnfile) > 2:
            cmd = "pxrms -s "+alnfile+" -n "+",".join(list(filt))+" > "+alnfile+".filt"
            print(cmd)
            os.system(cmd)
