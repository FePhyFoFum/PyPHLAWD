import sys
import tree_reader
import os
import sqlite3


def phyname(nm):
    return nm.replace("'","").replace(" ","_").replace(":","_").replace(",","_").replace("(","_").replace(")","_").replace("[","_").replace("]","_").replace(";","_")


def get_ncbi_names(DB, ncbilist):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    idn = {}
    for i in ncbilist:
        c.execute("select name from taxonomy where ncbi_id = ? and name_class = 'scientific name'",(i,))
        l = c.fetchall()
        for j in l:
            tname = str(j[0])
            idn[i] = tname
    return idn

def get_ott_names(taxfile, ottlist):
    tab = open(sys.argv[1],"r")
    idn = {} #ncbi is key, ott is value
    count = 0
    for i in tab:
        if count % 1000000 == 0:
            print count
        count += 1
        spls = i.split("\t|\t")
        try:
            idn["ott"+spls[0]] = spls[2].replace(" ","_")
        except:
            continue
    tab.close()
    return idn

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print "python "+sys.argv[0]+" ott_taxonomy.tsv db infile outfile"
        sys.exit(0)
    ottids = []
    ncbis = []
    for i in tree_reader.read_tree_file_iter(sys.argv[3]):
        for j in i.iternodes():
            if len(j.label) > 0:
                if "ott" in j.label:
                    ottids.append(j.label.replace("ott",""))
                else:
                    ncbis.append(j.label)

    # first do ott
    oidn = get_ott_names(sys.argv[1], ottids)

    # now do ncbi
    nidn = get_ncbi_names(sys.argv[2],ncbis)

    names_done = set()

    #first we do NCBI
    tree = tree_reader.read_tree_file_iter(sys.argv[3]).next()
    for j in tree.iternodes():
        if j.label in nidn:
            j.label = phyname(nidn[j.label])
            names_done.add(j.label)

    prune = set()
    #then we do ott
    outf = open(sys.argv[4],"w")
    for j in tree.iternodes():
        if j.label in oidn:
            if phyname(oidn[j.label]) in names_done:
                prune.add(j.label)
            else:
                j.label = phyname(oidn[j.label])
                names_done.add(j.label)
    outf.write(tree.get_newick_repr_note(True)+";")
    outf.close()
    
    cmd = "pxrmt -t "+sys.argv[-1]+" -n "+",".join(list(prune))+" > "+sys.argv[-1]+".pr.tre"
    print cmd
    os.system(cmd)
    """
    outf = open(sys.argv[4],"w")
    for i in tree_reader.read_tree_file_iter(sys.argv[3]):
        for j in i.iternodes():
            if j.label in oidn:
                j.label = phyname(oidn[j.label])
            elif j.label in nidn:
                j.label = phyname(nidn[j.label])
        outf.write(i.get_newick_repr_note(True)+";")
    outf.close()
   """
