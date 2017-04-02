import sys
import os
import seq

def make_info_table(clusterd,idn, outfile):
    cli = {}
    clns = []
    spls = {}
    for i in os.listdir(clusterd):
        if ".fa" not in i:
            continue
        sps = set()
        num = 0
        avl = 0
        for j in seq.read_fasta_file_iter(clusterd+"/"+i):
            sps.add(idn[j.name])
            if idn[j.name] not in spls:
                spls[idn[j.name]] = []
            spls[idn[j.name]].append(i)
            num += 1
        cli[i] = sps
        clns.append([i,len(sps)])
    clns = sorted(clns, key=lambda x: x[1], reverse=True)
    keep = []
    if len(spls) > 20:
        for i in clns:
            if i[1] >= 4:
                keep.append(i)
    else:
        keep = clns
    outfile = open(outfile,"w")
    outfile.write("species")
    for i in keep:
        outfile.write(","+i[0])
    outfile.write("\n")
    for j in spls:
        outfile.write(j)
        for i in keep:
            if j in cli[i[0]]:
                outfile.write(",x")
            else:
                outfile.write(",")
        outfile.write("\n")
    outfile.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "python "+sys.argv[0]+" maindir"
        sys.exit(0)

    cld = sys.argv[1]
    #take off the trailing slash if there is one
    if cld[-1] == "/":
        cld = cld[0:-1]
    idn = {}
    tf = open(cld+"/"+cld.split("/")[-1]+".table","r")
    for i in tf:
        spls = i.strip().split("\t")
        idn[spls[3]] = spls[4]
    tf.close()

    count = 0

    for root, dirs, files in os.walk(cld,topdown=False):
        if "clusters" in root:
            continue
        if "clusters" in dirs:
            make_info_table(root+"/clusters",idn, root+"/info.csv")
            count += 1
