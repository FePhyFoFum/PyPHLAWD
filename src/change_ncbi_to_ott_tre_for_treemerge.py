import sys
import tree_reader
import os

def get_ott_names_for_ncbi(taxfile, ncbilist):
    tab = open(sys.argv[1],"r")
    idn = {} #ncbi is key, ott is value
    count = 0
    for i in tab:
        if count % 1000000 == 0:
            print count
        count += 1
        spls = i.split("\t|\t")
        if "ncbi" in spls[4]:
            spls2 = spls[4].split(",")
            for j in spls2:
                if "ncbi" in j:
                    ncbiid = j.split(":")[1]
                    break
            if ncbiid in ncbilist:
                print ncbiid
                idn[ncbiid] = "ott"+spls[0]
                if len(idn) == ncbilist:
                    break
        else:
            continue
    tab.close()
    return idn

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print "python "+sys.argv[0]+" ott_taxonomy.tsv infile outfile"
        sys.exit(0)
    ncbis = []
    for i in tree_reader.read_tree_file_iter(sys.argv[2]):
        for j in i.iternodes():
            if len(j.label) > 0:
                ncbis.append(j.label)

    idn = get_ott_names_for_ncbi(sys.argv[1], ncbis)
    invalidchars = ":;[](),"

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
   
