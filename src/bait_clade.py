import sys
import os
from conf import DI
from clint.textui import colored
from logger import Logger
from add_clade_clusters import write_merge_table_and_temp_aln_file as wmtt
from add_clade_clusters import merge_alignments
import seq
import emoticons


def write_fasta_file(files,outfilen):
    outfile = open(outfilen,"w")
    for i in files:
        for j in seq.read_fasta_file_iter(i):
            outfile.write(j.get_fasta())
    outfile.close()

if __name__ == "__main__":
    if len(sys.argv) != 4 and len(sys.argv) != 5:
        print("python "+sys.argv[0]+" startdir tablefile logfile [TEMPDIR]")
        sys.exit(0)
    d = sys.argv[1]
    tablefile=sys.argv[2]
    LOGFILE = sys.argv[3]
    log = Logger(LOGFILE)
    
    # read the temp directory if there is one
    if len(sys.argv) == 4:
        TEMPDIR = "./"
    else:
        TEMPDIR = sys.argv[4]
        if TEMPDIR[-1] != "/":
            TEMPDIR += "/"
    
    outclu = d+"/clusters/"
    #TODO: need to make sure that the seqs that are in the DIR that aren't in the children get clustered and included here
    #   1 make a tempfile with the seqs that aren't in children
    #   2 cluster these as a single cluster
    #   3 add the results to the cluster directory
    dirs = [os.path.join(d,o) for o in os.listdir(d) if os.path.isdir(os.path.join(d,o))]
    joinseqs = {}
    for c in dirs:
        if "environmental" in c or "clusters" in c:
            continue
        print(colored.green("  ADDING"),c,colored.green(emoticons.get_ran_emot("meh")))
        cur =  c+"/clusters"
        for i in os.listdir(cur):
            if i[-3:] == ".fa":
                if i not in joinseqs:
                    joinseqs[i] = []
                joinseqs[i].append(cur+"/"+i)
    for i in joinseqs:
        print(colored.green("    MERGING"),i,colored.green(emoticons.get_ran_emot("meh")))
        write_fasta_file(joinseqs[i],outclu+i)
        wmtt([j.replace(".fa",".aln") for j in joinseqs[i]],TEMPDIR)
        merge_alignments(outclu+i.replace(".fa",".aln"),TEMPDIR)

    """
    cmd = "python "+DI+"get_internal_seqs_unrepresented_in_tips.py "+d+" "+LOGFILE
    os.system(cmd)
    cmd = "python "+DI+"add_internal_seqs_to_clusters.py "+d+" "+outclu+" "+LOGFILE
    os.system(cmd)
    """
