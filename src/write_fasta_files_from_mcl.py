"""
Read the concatenated fasta file either with or without ends cut
write individual fasta files for each cluster
"""

import sys,os
from seq import read_fasta_file
from tree_utils import get_name

def mcl_to_fasta(all_fasta,mcl_outfile,minimal_taxa,outdir):
    #print "Reading mcl output file"
    clusterDICT = {} #key is seqID, value is clusterID
    minimal_taxa = int(minimal_taxa)
    count = 0
    with open(mcl_outfile,"r") as infile:
        for line in infile:
            if len(line) < 3: continue #ignore empty lines
            spls = line.strip().split('\t')
            if len(set(get_name(i) for i in spls)) >= minimal_taxa:
                count += 1
                for seqID in spls:
                    clusterDICT[seqID] = str(count)
                    
    #print "Reading the fasta file",all_fasta
    for s in read_fasta_file(all_fasta):
        try:
            clusterID = clusterDICT[s.name]
            with open(outdir+"cluster"+clusterID+".fa","a") as outfile:
                outfile.write(">"+s.name+"\n"+s.seq+"\n")
        except: pass # Seqs that did not go in a cluster with enough taxa
    #print count,"clusters with at least",minimal_taxa,"taxa written to",outdir

if __name__ =="__main__":
    if len(sys.argv) != 5:
        print "usage: write_fasta_files_from_mcl.py all_fasta mcl_outfile minimal_taxa outDIR"
        sys.exit()
    
    mcl_to_fasta(all_fasta=sys.argv[1],mcl_outfile=sys.argv[2],\
                 minimal_taxa=int(sys.argv[3]),outdir=sys.argv[4])
    
