import os
import sys

import seq

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "python "+sys.argv[0]+" infile"
        sys.exit(0)
    

    lens = []
    for i in seq.read_fasta_file_iter(sys.argv[1]):
        print len(i)
    """    lens.append(len(i))
    print "mean",sum(lens)/float(len(lens))
    print "min",min(lens)
    print "max",max(lens)
    """
