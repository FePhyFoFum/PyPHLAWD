import sys
import tree_reader
import os

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print "python "+sys.argv[0]+" table infile outfile"
        sys.exit(0)
    tab = open(sys.argv[1],"r")
    idn = {}
    invalidchars = ":;[](),"
    for i in tab:
        spls = i.strip().split("\t")
        idn[spls[1]] = spls[4]
    tab.close()
    outf = open(sys.argv[3],"w")
    for i in tree_reader.read_tree_file_iter(sys.argv[2]):
        for j in i.iternodes():
            if j.label in idn:
                lab = idn[j.label]
                # check if quotes are required bc of invalid chars
                if any(elem in lab for elem in invalidchars):
                    #print "gotta quote this sucka: " + lab
                    lab = "\"" + lab + "\""
                else:
                    lab = lab.replace(" ","_")
                j.label = lab
        outf.write(i.get_newick_repr(True)+";")
    outf.close()
   
