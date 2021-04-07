import os
import sys
import argparse as ap
from clint.textui import colored
from datetime import datetime
from conf import DI
from conf import py
import emoticons
import tree_reader

def generate_argparser ():
    parser = ap.ArgumentParser(prog="setup_clade.py",
        formatter_class=ap.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-t", "--taxon", type=str,nargs=1, required=True,
        help=("The id or name of the taxon to be processes."), metavar=("ID/NAME"))
    parser.add_argument("-b", "--database", type=str, nargs=1, required=True,
        help=("Location of database."))
    parser.add_argument("-s", "--seqgzfolder", type=str,nargs=1,required=True,
        help=("Location of the gzseqs directory"))
    parser.add_argument("-o", "--outdir", type=str, nargs=1, required=True,
        help=("Location of the output directory (must already exist)."))
    parser.add_argument("-l", "--logfile", type=str, nargs=1, required=True,
        help=("Where to write the logfile."))
    parser.add_argument("-f", "--tlistf", type=str, nargs=1, required=False,
        help=("Taxon list file."))
    return parser

if __name__ == "__main__":
    parser = generate_argparser()
    args = parser.parse_args(sys.argv[1:])
    
    print(colored.blue("STARTING PYPHLAWD "+emoticons.get_ran_emot("excited")))
    start = datetime.now()
    
    dirl = args.outdir[0]
    if dirl[-1] == "/":
        dirl = dirl[:-1]
    
    taxon = args.taxon[0]
    db = args.database[0]

    # This will be used to limit the taxa
    taxalistf = None
    if args.tlistf is not None:
        taxalistf = args.tlistf[0]
        print(colored.yellow("LIMITING TO TAXA IN"),taxalistf)

    # Log file
    logfile = args.logfile[0]
    if logfile[-len(".md.gz"):] != ".md.gz":
        logfile += ".md.gz"

    gzfiles = args.seqgzfolder[0]
    if gzfiles[-1] != "/":
        gzfiles += "/"

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
    cmd = py+" "+DI+"populate_dirs_first.py "+tname+" "+dirl+" "+db+" "+gzfiles
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
