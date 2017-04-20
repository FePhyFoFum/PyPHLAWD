import sys
import math
from conf import length_limit
from conf import evalue_limit


def process_blast_out(infile,outfile=None):
    inf = open(infile,"r")
    ouf = None
    if outfile != None:
        ouf = open(outfile,"w")
    dclus = {}
    clus = set()
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
        dclus[spls[0]]=spls[2].split("___")[0]
        clus.add(spls[2].split("___")[0])
        if ouf != None:
            ouf.write(spls[0]+"\t"+spls[2]+"\t"+spls[14]+"\n")
    inf.close()
    if ouf != None:
        ouf.close()
    return dclus,clus

def process_blast_out_lce(infile, outfile = None):
    inf = open(infile, "r")
    ouf = None
    if outfile != None:
        ouf = open(outfile,"w")
    dclus = {}
    clus = set()
    for i in inf:
        spls = i.strip().split("\t")
        qlen = (max(float(spls[10]),float(spls[11]))-min(float(spls[10]),float(spls[11]))) / float(spls[1])
        slen = (max(float(spls[12]),float(spls[13]))-min(float(spls[12]),float(spls[13]))) / float(spls[3])
        if float(spls[14]) != 0:
            val = -math.log10(float(spls[14])) * qlen * slen
        else:
            val = 180 * qlen * slen
        if val < -math.log(evalue_limit):
            continue
        dclus.add(spls[2].split("___")[0])
        clus.add(spls[2].split("___")[0])
        if ouf != None:
            ouf.write(spls[0]+"\t"+spls[2]+"\t"+spls[14]+"\n")
    inf.close()
    if ouf != None:
        ouf.close()
    return dclus,clus

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "python "+sys.argv[0]+" infile.rawblast outfile.mclin"
        sys.exit(0)
    process_blast_out(sys.argv[1],sys.argv[2])
