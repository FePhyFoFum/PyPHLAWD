import sys
import math

def process_blast_out(infile,outfile):
    inf = open(infile,"r")
    ouf = open(outfile,"w")
    clus = set()
    for i in inf:
        spls = i.strip().split("\t")
        if min(float(spls[1]),float(spls[3]))/max(float(spls[1]),float(spls[3])) < 0.75:
            continue
        if (max(float(spls[10]),float(spls[11]))-min(float(spls[10]),float(spls[11]))) / float(spls[1]) < 0.75:
            continue
        if (max(float(spls[12]),float(spls[13]))-min(float(spls[12]),float(spls[13]))) / float(spls[3]) < 0.75:
            continue
        if float(spls[14]) != 0:
            if -math.log10(float(spls[14])) < 20:
                continue
        ouf.write(spls[0]+"\t"+spls[2]+"\t"+spls[14]+"\n")
    inf.close()
    ouf.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "python "+sys.argv[0]+" infile.rawblast outfile.mclin"
        sys.exit(0)
    process_blast_out(sys.argv[1],sys.argv[2])
