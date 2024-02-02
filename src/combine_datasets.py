import sys
import os

from conf import perc_identity,evalue_limit,nthread
from add_outgroup_to_matrix import construct_db_of_parts

def run_blast(blastdb,filen):
    cmd = "blastn -task blastn -db "+blastdb+".db -query "+filen+" -perc_identity "+str(perc_identity)+" -evalue "+str(evalue_limit)+" -num_threads "+str(nthread)+" -max_target_seqs 10000000 -out "+filen+".rawblastn -outfmt '6 qseqid qlen sseqid slen frames pident nident length mismatch gapopen qstart qend sstart send evalue bitscore'"
    os.system(cmd)
    #os.remove(blastdb+".db.nhr")
    #os.remove(blastdb+".db.nin")
    #os.remove(blastdb+".db.nsq")
    return filen+".rawblastn"

def process_blast(infile):
    of = open(infile,"r")
    finaldict = {} # key taxonid, value dict, key genename, value seqid
    finaldictval = {} # key taxonid, value dict, key genename, value bitscore
    for i in of:
        spls = i.strip().split("\t")
        matchedgene = spls[2].split("___")[0]
        querytaxon = spls[0]
        matchvalue = float(spls[-1])
        try:
            finaldict[querytaxon]
        except:
            finaldict[querytaxon] = {}
            finaldictval[querytaxon] = {}
        try:
            x = finaldictval[querytaxon][matchedgene]
            if matchvalue > x:
                finaldict[querytaxon][matchedgene] = spls[0]
                finaldictval[querytaxon][matchedgene] = matchvalue
        except:
            finaldict[querytaxon][matchedgene] = spls[0]
            finaldictval[querytaxon][matchedgene] = matchvalue
    of.close()
    os.remove(infile)
    return finaldict

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("python",sys.argv[0],"dataset1","dataset2")
        sys.exit(0)

    fl1 = sys.argv[1]
    fl1p = open(sys.argv[1].replace("outaln","outpart"),"r")
    fl2 = sys.argv[2]
    fl2p = open(sys.argv[2].replace("outaln","outpart"),"r")
    print(fl1,fl1p,fl2,fl2p)
    blastdb,parts,genesfn = construct_db_of_parts(fl1,fl1p,"TEST") # this will be based on names
    blastdb2,parts2,genesfn2 = construct_db_of_parts(fl2,fl2p,"TEST2") # this will be based on names
    for i in genesfn.values():
        print(i)
        blastoutput = run_blast(blastdb2,i)
        finaldict = process_blast(blastoutput)
        print(finaldict)
    #    print(i)
