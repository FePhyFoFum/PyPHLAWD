import os
import sys
import trim_tips
import seq

if __name__ == "__main__":
    if len(sys.argv) != 7:
        print "python "+sys.argv[0]+" file.tre aln relative_cutoff absolute_cutoff outtre outaln"
        sys.exit(0)

    treefile = sys.argv[1]
    alnfile = sys.argv[2]
    rel_cut = sys.argv[3]
    abs_cut = sys.argv[4]
    outtree = open(sys.argv[5],"w")
    tree,removed = trim_tips.main(treefile,rel_cut,abs_cut)
    outtree.write(tree.get_newick_repr(True)+";\n")
    outtree.close()
    outaln = open(sys.argv[6],"w")
    for i in seq.read_fasta_file_iter(alnfile):
        if i.name not in removed:
            outaln.write(i.get_fasta())
    outaln.close()

