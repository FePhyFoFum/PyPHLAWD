import sys
import os
import random
import networkx as nx
import matplotlib.pyplot as plt

import seq
from conf import perc_identity,evalue_limit,nthread

print(perc_identity,evalue_limit)
def run_blast(blastdb,filen):
    cmd = "blastn -task blastn -db "+blastdb+".db -query "+filen+" -perc_identity "+str(perc_identity)+" -evalue "+str(evalue_limit)+" -num_threads "+str(nthread)+" -max_target_seqs 10000000 -out "+filen+".rawblastn -outfmt '6 qseqid qlen sseqid slen frames pident nident length mismatch gapopen qstart qend sstart send evalue bitscore' 2> NOPE"
    os.system(cmd)
    #os.remove(blastdb+".db.nhr")
    #os.remove(blastdb+".db.nin")
    #os.remove(blastdb+".db.nsq")
    return filen+".rawblastn"

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
                genesf[j].write(">"+i.name+"\n"+i.seq[b-1:e].replace("-","")+"\n")
    tempoutf.close()
    for i in genesn:
        genesf[name].close()
    cmd = "makeblastdb -in "+dbfn+" -out "+dbfn+".db -dbtype nucl"# > /dev/null 2>&1"
    os.system(cmd)
    os.remove(dbfn)
    return dbfn,genes,genesfn

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
    #os.remove(infile)
    return finaldict

def get_gene_ids(infile):
    ids = list(seq.read_fasta_file_return_dict(infile).keys())
    return ids

def get_seq_from_file(s,infile):
    d = seq.read_fasta_file_return_dict(infile)
    return d[s].seq.replace("-","")
    

class NewGene:
    def __init__(self):
        self.geneset = set([])
        self.genes = {}

    def addgene(self,la,fl):
        self.genes[la] = fl

    def issame(self,gene1,gene2):
        if gene1 in self.geneset:
            self.geneset.add(gene2)
            return True
        if gene2 in self.geneset:
            self.geneset.add(gene1)
            return True
        return False

    def writefile(self,fn):
        fn = open(fn,"w")
        for i in self.genes:
            fn.write(">"+i+"\n"+get_seq_from_file(i,self.genes[i])+"\n")
        fn.close()

    def __str__(self):
        return ",".join(list(self.geneset))

def generate_dataset(tips,files,outf):
    ngs = []
    for i in tips:
        for j in files[i]:
            lj = list(j['lg'].values())
            if len(ngs) == 0:
                n = NewGene()
                n.geneset.add(lj[0])
                n.geneset.add(lj[1])
                n.addgene(i,j['lg'][i])
                ngs.append(n)
            else:
                t = False
                for k in ngs:
                    if k.issame(lj[0],lj[1]):
                        k.addgene(i,j['lg'][i])
                        t = True
                        break
                if t == False:
                    n = NewGene()
                    n.geneset.add(lj[0])
                    n.geneset.add(lj[1])
                    n.addgene(i,j['lg'][i])
                    ngs.append(n)
    count = 0 
    ffs = []
    for i in ngs:
        print(i)
        i.writefile(outf+str(count))
        ff = outf+str(count)+".aln"
        ffs.append(ff)
        cmd = "mafft --adjustdirectionaccurately "+outf+str(count)+" | sed 's/_R_//g' > "+ff
        os.system(cmd)
        count += 1
    cmd = "pxcat -s "+" ".join(ffs)+" -o TEMPTEMPCAT -p TEMPTEMPPART"
    os.system(cmd)
    return

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("python",sys.argv[0],"dataset1","dataset2")
        sys.exit(0)

    flt = []
    fls = sys.argv[1:]
    flp = []
    for i in fls:
        flt.append(get_gene_ids(i))
        flp.append(open(i.replace("outaln","outpart"),"r"))
    bdbs = []
    prts = []
    gens = []
    count = 0
    for i,j in zip(fls,flp):
        blastdb,parts,genesfn = construct_db_of_parts(i,j,"TEST"+str(count)) # this will be based on names
        bdbs.append(blastdb)
        prts.append(parts)
        gens.append(genesfn)
        count += 1
    biggraph = nx.MultiGraph()
    for i in flt:
        for j in i:
            biggraph.add_node(j)
    count = 0
    for i in gens:
        for j in i:
            for k in range(len(bdbs)):
                if k > count:
                    blastoutput = run_blast(bdbs[k],i[j])
                    finaldict = process_blast(blastoutput)
                    if len(finaldict) > 0:
                        g = list(list(finaldict.values())[0].keys())[0]
                        ids = get_gene_ids(g)
                        for l in finaldict:
                            for m in ids:
                                biggraph.add_edge(l,m,lg={l:j,m:g})
                                #print(biggraph[l][m])
        count += 1
    potential_tips = []
    count = 0
    for i in flt:
        most = 0
        mostn = {}
        for j in i:
            be = biggraph.edges(j)
            for k in be:
                n = len(biggraph[k[0]][k[1]])
                if n > most:
                    most = n
        #sys.exit(0)
        for j in i:
            be = biggraph.edges(j)
            #print(be)
            for k in be:
                if len(biggraph[k[0]][k[1]]) == most:
                    mostn[k[0]] = []
                    for l in biggraph[k[0]][k[1]]:
                        mostn[k[0]].append(biggraph[k[0]][k[1]][l])
        potential_tips.append(mostn)
        #print(mostn)
        count += 1
    tips = []
    vals = {}
    for i in potential_tips:
        x = random.choice(list(i.keys()))
        #print(x,i[x])
        tips.append(x)
        vals[x]=i[x]
    generate_dataset(tips,vals,"TEMPTEMP.fa")
