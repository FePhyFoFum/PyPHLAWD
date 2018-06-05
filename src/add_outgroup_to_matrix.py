import sys
import os
import argparse as ap

from conf import perc_identity,evalue_limit,nthread
import seq
from get_subset_genbank import make_files_with_id as mfid

import platform
plat = platform.platform()
mac = False
if "Darwin" in plat:
    mac = True


def construct_db_of_sister(taxon,DB,outprefix):
    outfile = outprefix+".tempfa"
    outfiletbl = outprefix+".temptable"
    mfid(taxon,DB,outfile,outfiletbl,remove_genomes=True)
    of = open(outfiletbl,"r")
    seq_taxon_dict = {}
    taxon_seqs_dict = {}
    for i in of:
        spls = i.strip().split("\t")
        try:
            taxon_seqs_dict[spls[1]]
        except:
            taxon_seqs_dict[spls[1]] = set()
        seq_taxon_dict[spls[3]] = spls[1]
        taxon_seqs_dict[spls[1]].add(spls[3])
    of.close()
    seqs_dict = seq.read_fasta_file_return_dict(outfile)
    return outfile,outfiletbl,seq_taxon_dict,taxon_seqs_dict,seqs_dict

def construct_db_of_parts(infile,infileparts,outprefix):
    genes = {} #name,[beg,end]
    genesn = []
    genesfn = {} #key name, value temp name
    genesf = {} #key name, value open file
    dbfn = outprefix+".tempdbfa"
    tempoutf = open(dbfn,"w")
    for i in infileparts:
        spls = i.strip().split(" ")
        name = spls[1]
        shortname = name.split("/")[-1]
        rnges = spls[-1].split("-")
        beg = int(rnges[0])
        end = int(rnges[1])
        genes[name] = [beg,end]
        genesn.append(name)
        genesfn[name] = outprefix+"."+shortname #open file should be the shortname
        genesf[name] = open(genesfn[name],"w")
    for i in seq.read_fasta_file_iter(infile):
        for j in genesn:
            b,e = genes[j]
            if len(i.seq[b-1:e].replace("-","")) > 100:
                tempoutf.write(">"+j+"___"+i.name+"\n"+i.seq[b-1:e].replace("-","")+"\n")
                genesf[j].write(">"+i.name+"\n"+i.seq[b-1:e]+"\n")
    tempoutf.close()
    for i in genesn:
        genesf[name].close()
    cmd = "makeblastdb -in "+dbfn+" -out "+dbfn+".db -dbtype nucl > /dev/null 2>&1"
    os.system(cmd)
    os.remove(dbfn)
    return dbfn,genes,genesfn

def run_blast(blastdb,filen):
    cmd = "blastn -db "+blastdb+".db -query "+filen+" -perc_identity "+str(perc_identity)+" -evalue "+str(evalue_limit)+" -num_threads "+str(nthread)+" -max_target_seqs 10000000 -out "+filen+".rawblastn -outfmt '6 qseqid qlen sseqid slen frames pident nident length mismatch gapopen qstart qend sstart send evalue bitscore'"
    os.system(cmd)
    os.remove(blastdb+".db.nhr")
    os.remove(blastdb+".db.nin")
    os.remove(blastdb+".db.nsq")
    return filen+".rawblastn"

def process_blast(infile,seq_taxon_dict,taxon_seqs_dict,parts):
    of = open(infile,"r")
    finaldict = {} # key taxonid, value dict, key genename, value seqid
    finaldictval = {} # key taxonid, value dict, key genename, value bitscore
    for i in of:
        spls = i.strip().split("\t")
        matchedgene = spls[2].split("___")[0]
        querytaxon = seq_taxon_dict[spls[0]]
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

def create_new_matrix(finaldict,seqsdict,genesn,outprefix,minover,maxtax):
    taxongenes = {} #key taxonid, value number of genes
    for i in finaldict:
        taxongenes[i] = len(finaldict[i])
    ordereddict = []
    for key, value in sorted(taxongenes.iteritems(), key=lambda (k,v): (v,k)):
        ordereddict.append(key)
    ordereddict = ordereddict[::-1]
    keep = []
    for i in ordereddict:
        if taxongenes[i] < minover:
            continue
        if len(keep) == maxtax:
            break
        keep.append(i)
    print "found ",len(keep),"to add"
    concats = {} # filename,partname
    temps = set() # files that are created that we want to delete later
    n = 0 # the tempfile counter
    savedseqstable = open(outprefix+".table","w")
    for i in genesn:
        #print i,genesn[i]
        tempadd = open(outprefix+".tempadd","w")
        count = 0
        for j in keep:
            if i in finaldict[j]:
                tempadd.write(">"+j+"\n"+seqsdict[finaldict[j][i]].seq+"\n")
                savedseqstable.write("X"+"\t"+j+"\t"+finaldict[j][i]+"\n")
                count += 1
        tempadd.close()
        gn = genesn[i]
        if count > 0:
            gn = outprefix+".tempadd"+str(n)
            temps.add(gn)
            cmd = "mafft --thread "+str(nthread)+" --quiet --adjustdirection --add "+outprefix+".tempadd "+genesn[i]+" > "+gn
            #print cmd
            os.system(cmd)
            if mac == False:
                os.system("sed -i 's/_R_//g' "+gn)
            else:
                os.system("sed -i '' 's/_R_//g' "+gn)
            n += 1
        concats[gn] = i
    savedseqstable.close()
    os.remove(outprefix+".tempadd")
    cmd = "pxcat -s "+" ".join(concats.keys())+" -o "+outprefix+".outaln -p "+outprefix+".tempparts"
    #print cmd
    os.system(cmd)
    #write the old parts file
    of = open(outprefix+".tempparts","r")
    of2 = open(outprefix+".outpart","w")
    for i in of:
        spls = i.strip().split(" ")
        of2.write(spls[0]+" "+concats[spls[1]]+" "+" ".join(spls[2:])+"\n")
    of2.close()
    of.close()
    #cleaning things
    os.remove(outprefix+".tempparts")
    for i in genesn:
        os.remove(genesn[i])
    for i in temps:
        os.remove(i)
    return

def generate_argparser():
    parser = ap.ArgumentParser(prog="add_outgroup_to_matrix.py",
        formatter_class=ap.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-b","--database",type=str,required=True,
        help=("Database with sequences."))
    parser.add_argument("-m","--matrix",type=str,required=True,
        help=("Concatenated matrix probably from find_good_clusters_for_concat.py"))
    parser.add_argument("-p","--parts",type=open,required=True,
        help=("The partition file probably from find_good_clusters_for_concat.py"))
    parser.add_argument("-t","--taxon",type=int,required=True,
        help=("The taxon (use the NCBI taxon id) to add."))
    parser.add_argument("-o","--outprefix",type=str,required=True,
        help=("The output file prefix."))
    parser.add_argument("-mn","--minoverlap",type=int,required=False,default=1)
    parser.add_argument("-mx","--maxtaxa",type=int,required=False,default=1)
    return parser

def main():
    parser = generate_argparser()
    if len(sys.argv[1:]) == 0:
        sys.argv.append("-h")
    args = parser.parse_args(sys.argv[1:])
    DB = args.database
    outprefix = args.outprefix
    print >> sys.stderr, "constructing a database of "+str(args.taxon)
    filen,filentable,seq_taxon_dict,taxon_seqs_dict,seqsdict = construct_db_of_sister(args.taxon,DB,outprefix)
    print >> sys.stderr, "constructing a database of the matrix"
    blastdb,parts,genesfn = construct_db_of_parts(args.matrix,args.parts,outprefix)
    print >> sys.stderr, "running blast"
    blastoutput = run_blast(blastdb,filen)
    print >> sys.stderr, "processing blast"
    finaldict = process_blast(blastoutput,seq_taxon_dict,taxon_seqs_dict,parts)
    print >> sys.stderr,"constructing the new matrix"
    create_new_matrix(finaldict,seqsdict,genesfn,outprefix,args.minoverlap,args.maxtaxa)
    
    #cleaning things
    os.remove(filen)
    os.remove(filentable)
    os.remove(filen+".genomes")

if __name__ == "__main__":
    main()
