import sys
import tree_reader

nbins = 20
newmax = 1.5

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "python "+sys.argv[0]+" infile outfile"
        sys.exit(0)
    tree = None
    inf = open(sys.argv[1],"r")
    for i in inf:
        if "MEDUSA_TREE" in i:
            i = i.strip().split(" ")[4].strip()
            tree = tree_reader.read_tree_string(i)
            break
    inf.close()
    minr = 0
    maxr = 0
    for i in tree.iternodes():
        if len(i.note) > 0:
            spls = i.note.split(",")
            for j in spls:
                if "r.mean" in j:
                    spls2 = j.split("=")
                    nm = float(spls2[1])
                    if nm > newmax:
                        nm = newmax
                    i.data["rate"] = nm
                    if nm > maxr:
                        maxr = nm
                        print "changed max:",nm
                    if nm < minr:
                        minr = nm
                        print "changed min:",nm
    bins = maxr/float(nbins)
    bins = newmax/float(nbins)
    print "bins:",bins
    for i in tree.iternodes():
        if len(i.note) > 0:
            if i.data["rate"] == 0:
                i.note += ",r.bin=0"
            else:
                i.note += ",r.bin="+str(int(i.data["rate"]/bins))
            i.note += ",r.nmax="+str(float(i.data["rate"]))
            
    ouf = open(sys.argv[2],"w")
    ouf.write("#NEXUS\nbegin trees;\n\ttree MEDUSA_TREE = [&R] ")
    ouf.write(tree.get_newick_repr_note(True)+";\nend;\n")
    ouf.close()
