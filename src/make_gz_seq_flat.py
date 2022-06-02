import sys
import os
import gzip
import argparse

def process_seqs(inf, maxsize,outd):
    fl = gzip.open (inf,"r")
    if os.path.exists(outd+"seqs."+inf.split("/")[-1]):
        return
    outf = gzip.open(outd+"seqs."+inf.split("/")[-1],"wt")
    new = False
    locus = None
    title = None
    defi = None
    taxonid = None
    length = 0
    descr = False
    seq = None
    seqst = False
    count =0
    added = 0
    for i in fl:
        i = str(i.decode())#or decode
        if descr == True:
            if "ACCESSION" in i:
                descr = False
            else:
                defi += " "+i.strip()
        if seqst == True:
            if "//" == i[0:2]:
                new = False
                if maxsize != None:
                    if len(seq) > maxsize:
                        continue
                if length != len(seq):
                    print("PROBLEM (SKIPPING):",locus+" ",length,len(seq))
                else:
                    print(locus+" "+seq,file=outf)
                    added += 1
            else:
                seq += "".join(i.strip().split()[1:])
        if "LOCUS" ==  i[0:5]:
            locus = i.strip().split()[1]
            #print(locus)
            try:
                length = int(i.strip().split()[2])
            except:
                print(i)
                sys.exit(0)
            new = True
        elif "DEFINITION" in i:
            defi = i.replace("DEFINITION  ","").strip()
            descr = True
        elif "ORIGIN" in i:
            seqst = True
            seq = ""
        elif "db_xref=" in i and "taxon" in i:
            try:
                taxonid = i.replace('"',"").strip().replace("'","").split("taxon:")[1]
            except:
                print(i)
                continue
    fl.close()
    outf.close()
    print("    added ",added,"seqs")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-o", "--outdir",help="Which directory?",required=True)
    parser.add_argument("-f", "--gzfilesdir",help="Where are the gzfiles",required=True)
    parser.add_argument("-m", "--maxsize",help="Don't keep seqs with length great than ",default=0,required=False)

    
    if len(sys.argv[1:]) == 0:
        sys.argv.append("-h")

    args = parser.parse_args()
    
    maxsize = int(args.maxsize)
    if maxsize == 0:
        maxsize = None

    std = args.outdir
    if std[-1] != "/":
        std += "/"

    kd = args.gzfilesdir
    if kd[-1] != "/":
        kd += "/"

    if std == kd:
        print("COME ON?! Same input and output dir?")
        sys.exit(0)

    for i in os.listdir(kd):
        print(i)
        process_seqs(kd+i,maxsize,std)
