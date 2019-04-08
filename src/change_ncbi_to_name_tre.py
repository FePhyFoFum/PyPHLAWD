import sys
import tree_reader
import os
from utils import newick_name
import argparse as ap

def generate_argparser():
    parser = ap.ArgumentParser(prog="change_ncbi_to_name_tre.py",
        formatter_class=ap.ArgumentDefaultsHelpFormatter)
    parser = ap.ArgumentParser()
    parser.add_argument("-t", "--table", type=str, help="NCBI translation table", required=True)
    parser.add_argument("-i", "--infile", type=str, help="Input tree", required=True)
    parser.add_argument("-o", "--outfile", type=str, help="Output tree", required=True)
    return parser

if __name__ == "__main__":
    parser = generate_argparser()
    if len(sys.argv[1:]) == 0:
        sys.argv.append("-h")
    args = parser.parse_args(sys.argv[1:])
    
    tab = open(args.table,"r")
    idn = {}
    for i in tab:
        spls = i.strip().split("\t")
        idn[spls[1]] = spls[4]
    tab.close()
    outf = open(args.outfile,"w")
    for i in tree_reader.read_tree_file_iter(args.infile):
        for j in i.iternodes():
            if j.label in idn:
                j.label = newick_name(idn[j.label])
        outf.write(i.get_newick_repr(False)+";")
    outf.close()
