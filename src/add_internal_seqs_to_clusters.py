"""
if there are seqs that are in the internal node file that aren't in the childnre
they will be added by this

this is typically done after you have done the clustering from the children
"""
import sys
import os
import seq
from logger import Logger
from add_clade_clusters import make_blast_db_from_cluster,merge_alignments,blast_file_against_db
from conf import tempname
import math


def add_ind_mafft(seq,cl_file):
    tf = open(cl_file,"a")
    tf.write(seq.get_fasta())
    tf.close()
    #make temp
    tf = open("subMSAtable","w")
    tf2 = open("temp.mergealn","w")
    count = 1
    for i in seq.read_fasta_file_iter(cl_file.replace(".fa",".aln")):
        tf2.write(i.get_fasta())
        tf.write(str(count)+" ")
        count += 1
    tf2.write(seq.get_fasta())
    tf.close()
    tf2.close()
    merge_alignments(cl_file.replace(".fa",".aln"))

def process_blast_ind():
    inf = open(tempname+".rawblastn","r")
    clus = {}
    reps_clus = set()
    for i in inf:
        spls = i.strip().split("\t")
        #get this test from internal_conf
        if min(float(spls[1]),float(spls[3]))/max(float(spls[1]),float(spls[3])) < 0.75:
            continue
        if (max(float(spls[10]),float(spls[11]))-min(float(spls[10]),float(spls[11]))) / float(spls[1]) < 0.75:
            continue
        if (max(float(spls[12]),float(spls[13]))-min(float(spls[12]),float(spls[13]))) / float(spls[3]) < 0.75:
            continue
        if float(spls[14]) != 0:
            if -math.log10(float(spls[14])) < 20:
                continue
        clus[spls[0]]=spls[2].split("___")[0]
        reps_clus.add(spls[2].split("___")[0])
    inf.close()
    return clus,reps_clus

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print "python "+sys.argv[0]+" indir outclu logfile"
        sys.exit(0)
    curfas = sys.argv[1]+"/notinchildren.fas"
    outclu = sys.argv[2]
    LOGFILE = sys.argv[3]
    log = Logger(LOGFILE)
    log.a()
    slen = 0
    seqs = seq.read_fasta_file(curfas)
    if len(seqs)> 0:
        seqd = {}
        for i in seqs:
            seqd[i.name] = i
        log.w("UNCLUSTERED SEQS IN "+sys.argv[1])
        #make blastdb of the cluster dir
        make_blast_db_from_cluster(outclu)
        blast_file_against_db(sys.argv[1],"notinchildren.fas")
        clus,reps_clus = process_blast_ind()
        for i in clus:
            add_ind_mafft(seqd[i],outclu+"/"+clus[i])
    log.c()
