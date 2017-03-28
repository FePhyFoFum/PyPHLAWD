import seq
import sys

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "python "+sys.argv[0]+" infile.fas"
        sys.exit(0)
    outfg = open(sys.argv[1]+".genomes","w")
    outfng = open(sys.argv[1]+".nogenomes","w")
    for i in seq.read_fasta_file_iter(sys.argv[1]):
        if len(i.seq) > 10000:
            outfg.write(i.get_fasta())
        else:
            outfng.write(i.get_fasta())
    outfg.close()
    outfng.close()
