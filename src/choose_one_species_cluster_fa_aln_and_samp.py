import sys
import seq
import os
import random
from logger import Logger
from conf import sampsize
from conf import dosamp

"""
right now this just chooses the longest

BEWARE, this writes over the file

it will also output a .samp file that will have a sample of at most 100
"""

if __name__ == "__main__":
    if len(sys.argv) != 4 and len(sys.argv) != 5:
        print("python "+sys.argv[0]+" table clusterdir fending+alnending [logfile]")
        sys.exit(0)
    ends = sys.argv[3].split("+")
    fend = ends[0]
    aend = ends[1]
    send = ".samp"
    LOGFILE = "pyphlawd.log"
    if len(sys.argv) == 5:
        LOGFILE = sys.argv[4]
    log = Logger(LOGFILE)
    log.a()
    tab = open(sys.argv[1],"r")
    idn = {}
    for i in tab:
        spls = i.strip().split("\t")
        idn[spls[2]] = spls[1]
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
        #gets the longest
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
        keep = []
        forsamp = []
        ssize = 0
        for i in seqs:
            for j in seqs[i]:
                fn.write(j.get_fasta())
                keep.append(j.name)
                forsamp.append(j)
                ssize += 1
        fn.close()
        #sample file
        # only make if it is bigger
        if ssize > sampsize and dosamp:
            x = random.sample(forsamp,sampsize)
            fn = open(dirr+"/"+o.replace(fend,send),"w")
            for i in x:
                fn.write(i.get_fasta())
            fn.close()
        #alignment file
        seqs = []
        total = 0
        for i in seq.read_fasta_file_iter(dirr+"/"+o.replace(fend,aend)):
            if i.name in keep:
                seqs.append(i)
                total += 1
        #print o,o.replace(fend,aend),len(keep),total
        fn = open(dirr+"/"+o.replace(fend,aend),"w")
        for i in seqs:
            fn.write(i.get_fasta())
        fn.close()
    log.c()
