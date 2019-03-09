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
from conf import length_limit
from conf import evalue_limit
import math
from conf import merge
import filter_blast

def add_ind_mafft(inseq,cl_file, merge,tempdir="./"):
    tf = open(cl_file,"a")
    tf.write(inseq.get_fasta())
    tf.close()
    #make temp
    if merge:
        tf = open(tempdir+"subMSAtable","w")
        tf2 = open(tempdir+"temp.mergealn","w")
        count = 1
        for i in seq.read_fasta_file_iter(cl_file.replace(".fa",".aln")):
            tf2.write(i.get_fasta())
            tf.write(str(count)+" ")
            count += 1
        tf2.write(inseq.get_fasta())
        tf.close()
        tf2.close()
        merge_alignments(cl_file.replace(".fa",".aln"),tempdir)

if __name__ == "__main__":
    if len(sys.argv) != 4 and len(sys.argv) != 5:
        print("python "+sys.argv[0]+" indir outclu logfile [TEMPDIR]")
        sys.exit(0)
    curfas = sys.argv[1]+"/notinchildren.fas"
    if os.path.isfile(curfas) == False:
        sys.exit(0)
    outclu = sys.argv[2]
    LOGFILE = sys.argv[3]
    log = Logger(LOGFILE)
    log.a()

    tempdir = "./"
    if len(sys.argv) == 5:
        tempdir = sys.argv[4]
        if tempdir[-1] != "/":
            tempdir += "/"

    slen = 0
    seqs = seq.read_fasta_file(curfas)
    if len(seqs)> 0:
        seqd = {}
        for i in seqs:
            seqd[i.name] = i
        log.w("UNCLUSTERED SEQS IN "+sys.argv[1])
        #make blastdb of the cluster dir
        make_blast_db_from_cluster(outclu,tempdir)
        blast_file_against_db(sys.argv[1],"notinchildren.fas",tempdir)
        dclus,clus = filter_blast.process_blast_out(tempdir+tempname+".rawblastn")
        for i in dclus:
            add_ind_mafft(seqd[i],outclu+"/"+dclus[i],merge,tempdir)
    log.c()
