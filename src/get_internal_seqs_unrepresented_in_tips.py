import sys
import os
import seq

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("python "+sys.argv[0]+" curdir logfile")
        sys.exit(0)
    curd = sys.argv[1]
    LOGFILE = sys.argv[2]

    ff = None
    dirs = []
    for i in os.listdir(curd):
        if ".fas" == i[-4:]:
            ff = i
        elif os.path.isdir(curd+"/"+i) and i != "clusters":
            dirs.append(curd+"/"+i+"/"+i+".fas")

    seqids = []
    seqs = {}
    for i in seq.read_fasta_file_iter(curd+"/"+ff):
        seqids.append(i.name)
        seqs[i.name] = i

    for i in dirs:
        for j in seq.read_fasta_file_iter(i):
            if len(j.name) > 0 and j.name in seqids:
                del seqs[j.name]

    if len(seqs) > 0:
        outfile = open(curd+"/notinchildren.fas","w")
        for i in seqs:
            outfile.write(seqs[i].get_fasta())
        outfile.close()


