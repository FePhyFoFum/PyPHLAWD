import sys
import seq
import os
import argparse as ap

def generate_argparser():
    parser = ap.ArgumentParser(prog="change_id_to_name_fasta.py",
        formatter_class=ap.ArgumentDefaultsHelpFormatter)
    parser = ap.ArgumentParser()
    parser.add_argument("-t", "--table", type=str, help="NCBI translation table", required=True)
    parser.add_argument("-i", "--infile", type=str, help="Input fasta alignment", required=True)
    parser.add_argument("-o", "--outfile", type=str, help="Output fasta alignment", required=True)
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
        idn[spls[3]] = spls[4]
    tab.close()
    outf = open(args.outfile, "w")
    for i in seq.read_fasta_file_iter(args.infile):
        i.name = idn[i.name].replace(" ","_")
        outf.write(i.get_fasta())
    outf.close()

