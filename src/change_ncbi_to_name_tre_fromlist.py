import sys
import tree_reader
import os
from utils import newick_name

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("python "+sys.argv[0]+" all_names.txt infile outfile")
        sys.exit(0)
    tab = open(sys.argv[1],"r")
    idn = {}
    for i in tab:
        spls = i.strip().split("\t")
        idn[spls[0]] = spls[3]
    tab.close()
    outf = open(sys.argv[3],"w")
    for i in tree_reader.read_tree_file_iter(sys.argv[2]):
        for j in i.iternodes():
            if j.label in idn:
                j.label = newick_name(idn[j.label])
        outf.write(i.get_newick_repr(True)+";")
    outf.close()
   
