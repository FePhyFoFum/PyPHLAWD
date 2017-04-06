import sys
import seq
import os

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print "python "+sys.argv[0]+" table infile..."
        sys.exit(0)

    tab = open(sys.argv[1],"r")
    idn = {}
    for i in tab:
        spls = i.strip().split("\t")
        idn[spls[3]] = spls[4]
    tab.close()
    for j in sys.argv[2:]:
        outf = open(j+".rn","w")
        for i in seq.read_fasta_file_iter(j):
            i.name = idn[i.name].replace(" ","_"),+"_"+i.name
            outf.write(i.get_fasta())
        outf.close()
       
