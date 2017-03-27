import sys
import seq
import os

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print "python "+sys.argv[0]+" table infile outfile"
        sys.exit(0)
    tab = open(sys.argv[1],"r")
    idn = {}
    for i in tab:
        spls = i.strip().split("\t")
        idn[spls[3]] = spls[4]
    tab.close()
    outf = open(sys.argv[3],"w")
    for i in seq.read_fasta_file_iter(sys.argv[2]):
        i.name = idn[i.name].replace(" ","_")
        outf.write(i.get_fasta())
    outf.close()
   