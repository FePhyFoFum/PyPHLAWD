import os
import sys
from clint.textui import colored
from datetime import datetime

from conf import DI
from conf import py
import emoticons
import tree_reader

if __name__ == "__main__":
    if len(sys.argv) != 5 and len(sys.argv) != 6:
        print("python "+sys.argv[0]+" taxon db outdir logfile [taxalist]")
        sys.exit(0)
    
    print(colored.blue("STARTING PYPHLAWD "+emoticons.get_ran_emot("excited")))
    start = datetime.now()
    dirl = sys.argv[3]
    if dirl[-1] == "/":
        dirl = dirl[:-1]
    taxon = sys.argv[1]
    db = sys.argv[2]
    # This will be used to limit the taxa
    taxalistf = None
    if len(sys.argv) == 6:
        taxalistf = sys.argv[5]
        print(colored.yellow("LIMITING TO TAXA IN"),sys.argv[5])

    # Log file
    logfile = sys.argv[4]
    if logfile[-len(".md.gz"):] != ".md.gz":
        logfile += ".md.gz"

    tname = dirl+"/"+taxon+".tre"
    if taxalistf != None:
        cmd = py+" "+DI+"get_ncbi_tax_tree_no_species.py "+taxon+" "+db+" "+taxalistf+" > "+tname
    else:
        cmd = py+" "+DI+"get_ncbi_tax_tree_no_species.py "+taxon+" "+db+" > "+tname
    print(colored.yellow("MAKING TREE"),taxon,colored.yellow(emoticons.get_ran_emot("excited")))
    os.system(cmd)
    trn = tree_reader.read_tree_file_iter(tname).__next__().label
    cmd = py+" "+DI+"make_dirs.py "+tname+" "+dirl
    print(colored.yellow("MAKING DIRS IN"),dirl,colored.yellow(emoticons.get_ran_emot("excited")))
    os.system(cmd)
    cmd = py+" "+DI+"populate_dirs_first.py "+tname+" "+dirl+" "+db
    if taxalistf != None:
        cmd += " "+taxalistf
    print(colored.yellow("POPULATING DIRS"),dirl,colored.yellow(emoticons.get_ran_emot("excited")))
    os.system(cmd)
    
    if os.path.isfile("log.md.gz"):
        os.remove("log.md.gz")
    cmd = py+" "+DI+"cluster_tree.py "+dirl+"/"+trn+"/ "+logfile
    os.system(cmd)
    
    print(colored.blue("PYPHLAWD DONE "+emoticons.get_ran_emot("excited")))
    end = datetime.now()
    print(colored.blue("Total time (H:M:S): "+str(end-start)+" "+emoticons.get_ran_emot("excited")))
    from utils import bcolors
    print(bcolors.HEADER, end=' ')
    emoticons.animate(emoticons.glasses_animated)
    print(bcolors.ENDC)

