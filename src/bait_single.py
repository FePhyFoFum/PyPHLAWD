import os
import sys
from logger import Logger
from conf import DI
from conf import evalue_limit
from conf import length_limit
from conf import perc_identity
from conf import nthread
from conf import takeouttaxondups
import math
import seq
from conf import tempname

def make_files(clus, infile, outfiledir):
    seqs = {}
    for i in seq.read_fasta_file_iter(infile):
        seqs[i.name] = i
    for i in clus:
        i = ".".join(i.split(".")[0:-1])+".fa"
        outf = open(outfiledir+"/"+i,"w")
        for j in clus[i]:
            outf.write(seqs[j].get_fasta())
        outf.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "python "+sys.argv[0]+" indir logfile"
        sys.exit(0)
    if sys.argv[1][-1] == "/":
        sys.argv[1]=sys.argv[1][:-1]
    sp = sys.argv[1].split("/")[-1]
    INFILE = sys.argv[1]+"/"+sp
    count = 0
    for i in seq.read_fasta_file_iter(INFILE+".fas"):
        count += 1
    if count == 0:
        sys.exit(0)
    LOGFILE = sys.argv[2]
    log = Logger(LOGFILE)
    cmd = "blastn -db "+tempname+".db -query "+INFILE+".fas -perc_identity "+str(perc_identity)+" -evalue "+str(evalue_limit)+" -num_threads "+str(nthread)+" -max_target_seqs 10000000 -out "+INFILE+".fasta.rawblastn -outfmt '6 qseqid qlen sseqid slen frames pident nident length mismatch gapopen qstart qend sstart send evalue bitscore'"
    log.wac("RUNNING "+cmd)
    os.system(cmd)

    #process the files 
    inf = open(INFILE+".fasta.rawblastn","r")
    clus = {}
    for i in inf:
        spls = i.strip().split("\t")
        if min(float(spls[1]),float(spls[3]))/max(float(spls[1]),float(spls[3])) < length_limit:
            continue
        if (max(float(spls[10]),float(spls[11]))-min(float(spls[10]),float(spls[11]))) / float(spls[1]) < length_limit:
            continue
        if (max(float(spls[12]),float(spls[13]))-min(float(spls[12]),float(spls[13]))) / float(spls[3]) < length_limit:
            continue
        if float(spls[14]) != 0:
            if -math.log10(float(spls[14])) < -math.log(evalue_limit):
                continue
        cl = spls[2].split("___")[0]
        if cl not in clus:
            clus[cl] = set()
        clus[cl].add(spls[0])
    inf.close()
    log.wac("MAKING FILES FROM BAIT")
    make_files(clus,INFILE+".fas",sys.argv[1]+"/clusters")

    cmd = "python "+DI+"align_tip_clusters.py "+sys.argv[1]+"/clusters "+LOGFILE
    log.wac("RUNNING "+cmd)
    os.system(cmd)
    if takeouttaxondups:
        cmd = "python "+DI+"choose_one_species_cluster_fa_aln_and_samp.py "+INFILE+".table "+sys.argv[1]+"/clusters .fa+.aln "+LOGFILE
        log.wac("RUNNING "+cmd)
        os.system(cmd)
