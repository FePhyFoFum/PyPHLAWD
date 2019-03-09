import os
import sys

from logger import Logger
from conf import DI
from conf import evalue_limit
from conf import perc_identity
from conf import nthread
from conf import takeouttaxondups
from conf import py

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("python "+sys.argv[0]+" indir logfile")
        sys.exit(0)
    if sys.argv[1][-1] == "/":
        sys.argv[1]=sys.argv[1][:-1]
    sp = sys.argv[1].split("/")[-1]
    INFILE = sys.argv[1]+"/"+sp
    LOGFILE = sys.argv[2]
    log = Logger(LOGFILE)

    if os.path.isfile( INFILE+".fas" ) == False:
        log.wac("NO DATA IN "+INFILE+".fas")
        sys.exit(0)
    else:
        if os.stat(INFILE+".fas").st_size == 0:
            log.wac("NO DATA IN "+INFILE+".fas")
            sys.exit(0)
    cmd = "makeblastdb -in "+INFILE+".fas -out "+INFILE+".db -dbtype nucl > /dev/null 2>&1"
    log.wac("RUNNING "+cmd)
    os.system(cmd)
    cmd = "blastn -db "+INFILE+".db -query "+INFILE+".fas -perc_identity "+str(perc_identity)+" -evalue "+str(evalue_limit)+" -num_threads "+str(nthread)+" -max_target_seqs 10000000 -out "+INFILE+".fasta.rawblastn -outfmt '6 qseqid qlen sseqid slen frames pident nident length mismatch gapopen qstart qend sstart send evalue bitscore'"
    log.wac("RUNNING "+cmd)
    os.system(cmd)
    cmd = py+" "+DI+"filter_blast.py "+INFILE+".fasta.rawblastn "+INFILE+".fasta.rawblastn.mclin"
    log.wac("RUNNING "+cmd)
    #cmd = "awk -F \"\t\" '{print $1\"\t\"$3\"\t\"$15}' "+INFILE+".fasta.rawblastn > "+INFILE+".fasta.rawblastn.mclin"
    os.system(cmd)
    cmd = "mcl "+INFILE+".fasta.rawblastn.mclin --abc --abc-neg-log10 -te 12 -tf 'gq(50)' -I 2.1 -o "+INFILE+".mclout > /dev/null 2>&1"
    log.wac("RUNNING "+cmd)
    os.system(cmd)
    cmd = py+" "+DI+"write_fasta_files_from_mcl.py "+INFILE+".fas "+INFILE+".mclout 1 "+sys.argv[1]+"/clusters/"
    log.wac("RUNNING "+cmd)
    os.system(cmd)
    cmd = "rm "+INFILE+".fasta.rawblastn "+INFILE+".db.n* "+INFILE+".fasta.rawblastn.mclin "+INFILE+".mclout"
    log.wac("CLEANING "+cmd)
    os.system(cmd)
    cmd = py+" "+DI+"align_tip_clusters.py "+sys.argv[1]+"/clusters "+LOGFILE
    log.wac("RUNNING "+cmd)
    os.system(cmd)
    if takeouttaxondups:
        cmd = py+" "+DI+"choose_one_species_cluster_fa_aln_and_samp.py "+INFILE+".table "+sys.argv[1]+"/clusters .fa+.aln "+LOGFILE
        log.wac("RUNNING "+cmd)
        os.system(cmd)
