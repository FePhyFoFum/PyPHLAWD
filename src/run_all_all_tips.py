import sys
import os

import tree_reader
import get_ncbi_tax_tree as gntt

def get_table_names(fl):
    f =open(fl,"r")
    d = {}
    for i in f:
        spls = i.strip().split("\t")
        d[spls[1]] = spls[4].replace(" ","_")+"_"+spls[1]
    f.close()
    return d

def check_aln(fl):
    r = False
    f = open(fl,"r")
    c = 0
    for i in f:
        if i[0] == ">":
            c += 1
    f.close()
    if c >= 2:
        r = True
    return r

def clean_name(s):
    s = s.replace(",","_")
    s = s.replace("&","_")
    s = s.replace("(","_")
    s = s.replace(")","_")
    s = s.replace("[","_")
    s = s.replace("]","_")
    s = s.replace(";","_")
    s = s.replace(":","_")
    return s

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("python",sys.argv[0],"tree db seqdir ogroupnum") # like corncorn ../../corn.db ../../gzzsseqs/corngzseqs 41934
        sys.exit(0)

    db = sys.argv[2]
    seqdir = sys.argv[3]
    ogroup = sys.argv[4]
    cmd1 = "python ~/apps/PyPHLAWD/src/setup_clade_ap.py -b "+db+" -s "+seqdir+" -t TAX -o . -l log"
    cmd2 = "python ~/apps/PyPHLAWD/src/find_good_clusters_for_concat_batch.py -i -d DIR -b "+db
    cmd3 = "python ~/apps/PyPHLAWD/src/add_outgroup_to_matrix.py -b "+db+" -m MATRIX -p PART -t TAX -o OUT -e EXT -s"+seqdir
    cmd4 = "iqtree -m GTR+G -s ALN -q PART -nt 4"

    t = tree_reader.read_tree_file_iter(sys.argv[1]).__next__()
    for i in t.leaves():
        lf = i
        ftax = ""
        if len(i.parent.children) == 1 and i.parent.label != "":
            ftax = i.parent.label
            lf = i.parent
        else:
            ftax = i.label
        tax = ftax.split("_")[-1]
        #if tax != "2961870" and tax != "122249" and tax != "179090" and tax != "19933":
        #    continue
        dir = tax+"_"+tax
        print(cmd1.replace("TAX",tax))
        os.system(cmd1.replace("TAX",tax))
        print(cmd2.replace("DIR",dir))
        os.system(cmd2.replace("DIR",dir))
        mat = dir+"/"+dir+"_outaln"
        part = dir+"/"+dir+"_outpart"
        if check_aln(mat) == False:
            print("too small")
            os.system("rm -r TEMPDIR*")
            continue
        otax = ogroup
        outm = mat+".outg"
        outp = mat+".outg.outpart"
        cc = cmd3.replace("MATRIX",mat).replace("PART",part).replace("OUT",outm).replace("TAX",otax).replace("EXT",tax)
        print(cc)
        os.system(cc)
        og = None
        f = open(outm+".table","r")
        for j in f:
            og = j.strip().split("\t")[1]
            break
        f.close()
        os.system(cmd4.replace("ALN",outm+".outaln").replace("PART",outp))
        tf = outm+".outpart.treefile"
        if og != None:
            os.system("pxrr -t "+tf+" -g "+og+" > "+tf+".rr")
            tf = tf+".rr"
            ttf = tree_reader.read_tree_file_iter(tf).__next__()
            rr = ttf.children[0]
            if og in rr.lvsnms():
                rr = ttf.children[1]
            tablenms = get_table_names(dir+"/"+dir+".table")
            for j in rr.leaves():
                j.label = clean_name(tablenms[j.label])
            ft = open(tf+".final","w")
            ft.write(rr.get_newick_repr(True)+";")
            ft.close()
        else:
            rr = tree_reader.read_tree_file_iter(tf).__next__()
            ft = open(tf+".final","w")
            ft.write(rr.get_newick_repr(True)+";")
            ft.close()
        os.system("rm -r TEMPDIR*")
