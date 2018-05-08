import sys
import os
from conf import DI
from conf import takeouttaxondups
from clint.textui import colored
from logger import Logger
import emoticons
import subprocess

if __name__ == "__main__":
    if len(sys.argv) != 4 and len(sys.argv) != 5:
        print "python "+sys.argv[0]+" startdir tablefile logfile [tempdir]"
        sys.exit(0)
    d = sys.argv[1]
    tablefile=sys.argv[2]
    LOGFILE = sys.argv[3]
    log = Logger(LOGFILE)

    TEMPDIR = "./"
    if len(sys.argv) == 5:
        TEMPDIR = sys.argv[4]
        if TEMPDIR[-1] != "/":
            TEMPDIR += "/"

    outclu = d+"/clusters/"
    #TODO: need to make sure that the seqs that are in the DIR that aren't in the children get clustered and included here
    #   1 make a tempfile with the seqs that aren't in children
    #   2 cluster these as a single cluster
    #   3 add the results to the cluster directory
    dirs = [os.path.join(d,o) for o in os.listdir(d) if os.path.isdir(os.path.join(d,o))]
    count = 0
    for c in dirs:
        if "environmental" in c or "clusters" in c:
            continue
        print colored.green("  ADDING"),c,colored.green(emoticons.get_ran_emot("meh"))
        cur =  c+"/clusters"
        cmd = "python "+DI+"add_clade_clusters.py "+cur+" "+outclu+" "+LOGFILE+" "+TEMPDIR
        rc = subprocess.call(cmd, shell=True)
        if rc != 0:
            print colored.red("  PROBLEM ADDING CLADE"),colored.red(emoticons.get_ran_emot("sad"))
            sys.exit(1)
        if takeouttaxondups:
            cmd = "python "+DI+"choose_one_species_cluster_fa_aln_and_samp.py "+tablefile+" "+outclu+" .fa+.aln "+LOGFILE
            os.system(cmd)
        # NEED TO DO SOMETHING ABOUT THE ALIGNMENT FILES
    print colored.green("   ADDING INTERNAL SEQS"),d,colored.green(emoticons.get_ran_emot("meh"))
    cmd = "python "+DI+"get_internal_seqs_unrepresented_in_tips.py "+d+" "+LOGFILE
    os.system(cmd)
    cmd = "python "+DI+"add_internal_seqs_to_clusters.py "+d+" "+outclu+" "+LOGFILE+" "+TEMPDIR
    os.system(cmd)
    
