import sys
import sqlite3
import tree_reader
from utils import newick_name
import argparse as ap

def generate_argparser():
    parser = ap.ArgumentParser(prog="change_ncbi_to_name_tre.py",
        formatter_class=ap.ArgumentDefaultsHelpFormatter)
    parser = ap.ArgumentParser()
    parser.add_argument("-d", "--db", type=str, help="NCBI database", required=True)
    parser.add_argument("-i", "--infile", type=str, help="Input tree", required=True)
    parser.add_argument("-o", "--outfile", type=str, help="Output tree", required=True)
    return parser

if __name__ == "__main__":
    parser = generate_argparser()
    if len(sys.argv[1:]) == 0:
        sys.argv.append("-h")
    args = parser.parse_args(sys.argv[1:])
    
    conn = sqlite3.connect(args.db)
    c = conn.cursor()
    idn = {}
    outf = open(args.outfile,"w")
    for i in tree_reader.read_tree_file_iter(args.infile):
        for j in i.iternodes():
            if j.label == "":
                continue
            c.execute("select name_class,edited_name from taxonomy where ncbi_id = ?", (j.label, ))
            nm = ""
            for k in c:
                if str(k[0]) == "scientific name":
                    nm = str(k[1])
            if nm != "":
                j.label = newick_name(nm)
        outf.write(i.get_newick_repr(True)+";")
    outf.close()
