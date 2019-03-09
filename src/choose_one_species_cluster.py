import sys
import seq
import os
from logger import Logger

"""
right now this just chooses the longest

BEWARE, this writes over the file
"""

if __name__ == "__main__":
    if len(sys.argv) != 4 and len(sys.argv) != 5:
        print("python "+sys.argv[0]+" table clusterdir fending [logfile]")
        sys.exit(0)
    fend = sys.argv[3]
    LOGFILE = "pyphlawd.log"
    if len(sys.argv) == 5:
        LOGFILE = sys.argv[4]
    log = Logger(LOGFILE)
    log.a()
    tab = open(sys.argv[1],"r")
    idn = {}
    for i in tab:
        spls = i.strip().split("\t")
        idn[spls[3]] = spls[4]
    tab.close()
    dirr = sys.argv[2]
    for o in os.listdir(dirr):
        if fend != None:
            if fend not in o:
                continue
        seqs = {}
        for i in seq.read_fasta_file_iter(dirr+"/"+o):
            if idn[i.name] not in seqs:
                seqs[idn[i.name]] = []
            seqs[idn[i.name]].append(i)
        for i in seqs:
            if len(seqs[i]) > 1:
                longest = None
                longestn = 0
                for j in seqs[i]:
                    if len(j.seq) > longestn:
                        longest = j
                        longestn = len(j.seq)
                seqs[i] = [longest]
        fn = open(dirr+"/"+o,"w")
        for i in seqs:
            for j in seqs[i]:
                fn.write(j.get_fasta())
        fn.close()
    log.c()
