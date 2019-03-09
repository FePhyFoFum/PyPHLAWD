import sys
import tree_reader
import os

def get_ncbi_names_for_ott(taxfile, ottlist):
    tab  = open(sys.argv[1],"r")
    idn = {} #ncbi is key, ott is value
    count = 0
    for i in tab:
        if count % 1000000 == 0:
            print(count)
        count += 1
        spls = i.split("\t|\t")
        try:
            ottlist[spls[0]]
        except:
            continue
        #if spls[0] not in ottlist:
        #    continue
        if "ncbi" in spls[4]:
            spls2 = spls[4].split(",")
            for j in spls2:
                if "ncbi" in j:
                    ncbiid = j.split(":")[1]
                    break
            idn["ott"+spls[0]] = ncbiid
            if len(idn) == len(ottlist):
                break
        else:
            continue
    tab.close()
    return idn

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("python "+sys.argv[0]+" ott_taxonomy.tsv infile outfile")
        sys.exit(0)
    otts = {}
    for i in tree_reader.read_tree_file_iter(sys.argv[2]):
        for j in i.iternodes():
            if len(j.label) > 0:
                if j.label[0:3] == "ott":
                    otts[j.label[3:]] = ""

    idn = get_ncbi_names_for_ott(sys.argv[1], otts)
    print(len(idn))

    outf = open(sys.argv[3],"w")
    for i in tree_reader.read_tree_file_iter(sys.argv[2]):
        for j in i.iternodes():
            if j.label in idn:
                j.label = idn[j.label]
        outf.write(i.get_newick_repr(True)+";")
    outf.close()
   
