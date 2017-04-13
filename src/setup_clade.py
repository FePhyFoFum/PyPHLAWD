import os
import sys
import tree_reader
from clint.textui import colored
from conf import DI
import emoticons

if __name__ == "__main__":
    if len(sys.argv) != 4 and len(sys.argv) != 5:
        print "python "+sys.argv[0]+" taxon db dirl [taxalist]"
        sys.exit(0)
    
    print colored.blue("STARTING PYPHLAWD "+emoticons.get_ran_emot("excited"))
    
    dirl = sys.argv[3]
    if dirl[-1] == "/":
        dirl = dirl[:-1]
    taxon = sys.argv[1]
    db = sys.argv[2]
    # This will be used to limit the taxa
    taxalistf = None
    if len(sys.argv) == 5:
        taxalistf = sys.argv[4]
        print colored.yellow("LIMITING TO TAXA IN"),sys.argv[4]

    tname = dirl+"/"+taxon+".tre"
    if taxalistf != None:
        cmd = "python "+DI+"get_ncbi_tax_tree_no_species.py "+taxon+" "+db+" "+taxalistf+" > "+tname
    else:
        cmd = "python "+DI+"get_ncbi_tax_tree_no_species.py "+taxon+" "+db+" > "+tname
    print colored.yellow("MAKING TREE"),taxon,colored.yellow(emoticons.get_ran_emot("excited"))
    os.system(cmd)
    trn = tree_reader.read_tree_file_iter(tname).next().label
    cmd = "python "+DI+"make_dirs.py "+tname+" "+dirl
    print colored.yellow("MAKING DIRS IN"),dirl,colored.yellow(emoticons.get_ran_emot("excited"))
    os.system(cmd)
    cmd = "python "+DI+"populate_dirs_first.py "+tname+" "+dirl+" "+db
    if taxalistf != None:
        cmd += " "+taxalistf
    print colored.yellow("POPULATING DIRS"),dirl,colored.yellow(emoticons.get_ran_emot("excited"))
    os.system(cmd)
    
    if os.path.isfile("log.md.gz"):
        os.remove("log.md.gz")
    cmd = "python "+DI+"cluster_tree.py "+dirl+"/"+trn+"/ log.md.gz"
    os.system(cmd)
    
    print colored.blue("PYPHLAWD DONE "+emoticons.get_ran_emot("excited"))


