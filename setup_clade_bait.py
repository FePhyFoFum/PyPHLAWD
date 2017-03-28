import os
import sys
import tree_reader
from clint.textui import colored
from conf import DI

if __name__ == "__main__":
    if len(sys.argv) != 5 and len(sys.argv) != 6:
        print "python "+sys.argv[0]+" taxon baitdir db dirl [taxalist]"
        sys.exit(0)
    
    dirl = sys.argv[4]
    if dirl[-1] == "/":
        dirl = dirl[:-1]
    taxon = sys.argv[1]
    baitdir = sys.argv[2]
    db = sys.argv[3]
    # This will be used to limit the taxa
    taxalistf = None
    if len(sys.argv) == 6:
        taxalistf = sys.argv[5]
        print colored.yellow("LIMITING TO TAXA IN"),sys.argv[4]

    tname = dirl+"/"+taxon+".tre"
    cmd = "python "+DI+"get_ncbi_tax_tree_no_species.py "+taxon+" "+db+" > "+tname
    print colored.yellow("MAKING TREE"),taxon
    os.system(cmd)
    trn = tree_reader.read_tree_file_iter(tname).next().label
    cmd = "python "+DI+"make_dirs.py "+tname+" "+dirl
    print colored.yellow("MAKING DIRS IN"),dirl
    os.system(cmd)
    cmd = "python "+DI+"populate_dirs_first.py "+tname+" "+dirl+" "+db
    if taxalistf != None:
        cmd += " "+taxalistf
    print colored.yellow("POPULATING DIRS"),dirl
    os.system(cmd)
    
    if os.path.isfile("log.md"):
        os.remove("log.md")
    cmd = "python "+DI+"bait_tree.py "+dirl+"/"+trn+"/ "+baitdir+" log.md"
    os.system(cmd)
