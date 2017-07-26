import sys
import os

#cmd = "python ~/Dropbox/programming/pyphlawd/src/summarize_overlap.py DIR/CLADE/ALN DIR/CLADE/TREE > OUTD"
cmd = "cp DIR/CLADE/RESULT.labeled.tre.qc OUTD"

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print "python "+sys.argv[0]+" finals.txt dir outdir"
        sys.exit(0)
    inf = open(sys.argv[1],"r")
    di = sys.argv[2]
    odi = sys.argv[3]
    clade = None
    tree = None
    aln = None
    for i in inf:
        if len(i.strip()) < 1 or i[0] == "#":
            continue
        if "export TREE=" in i:
            tree = i.strip().split("=")[1]
        elif "export ALN=" in i:
            aln = i.strip().split("=")[1]
            c = cmd.replace("DIR",di).replace("TREE",tree).replace("ALN",aln).replace("CLADE",clade).replace("OUTD",odi+"/"+clade+".tre")
            print c
            os.system(c)
        else:
            clade = i.strip()
    inf.close()
