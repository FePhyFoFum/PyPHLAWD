import sys
import os
import seq
import math
import networkx as nx
from clint.textui import colored
from shutil import copyfile,move
from logger import Logger
import platform
plat = platform.platform()
from conf import tempname
from conf import dosamp
from conf import nthread
from conf import length_limit,evalue_limit,perc_identity
import emoticons

nthread = str(nthread)

mac = False
if "Darwin" in plat:
    mac = True

use_merge = True

def make_blast_db_from_cluster(indir):
    outf = open(tempname,"w")
    for i in os.listdir(indir):
        if i[-3:] != ".fa":
            continue
        fn = i
        for j in seq.read_fasta_file_iter(indir+"/"+i):
            j.name = fn+"___"+j.name
            outf.write(j.get_fasta())
    outf.close()
    cmd = "makeblastdb -in "+tempname+" -out "+tempname+".db -dbtype nucl > /dev/null 2>&1"
    os.system(cmd)

def make_blast_db_from_cluster_samp(indir):
    outf = open(tempname,"w")
    for i in os.listdir(indir):
        if i[-3:] != ".fa":
            continue
        fn = i
        if os.path.isfile(indir+"/"+i.replace(".fa",".samp")):
            for j in seq.read_fasta_file_iter(indir+"/"+i.replace(".fa",".samp")):
                j.name = fn+"___"+j.name
                outf.write(j.get_fasta())
        else:
            for j in seq.read_fasta_file_iter(indir+"/"+i):
                j.name = fn+"___"+j.name
                outf.write(j.get_fasta())
    outf.close()
    cmd = "makeblastdb -in "+tempname+" -out "+tempname+".db -dbtype nucl > /dev/null 2>&1"
    os.system(cmd)


def blast_file_against_db(indir,filename):
    cmd = "blastn -db "+tempname+".db -query "+indir+"/"+filename+" -perc_identity "+str(perc_identity)+" -evalue "+str(evalue_limit)+" -num_threads "+nthread+" -max_target_seqs 10000000 -out "+tempname+".rawblastn -outfmt '6 qseqid qlen sseqid slen frames pident nident length mismatch gapopen qstart qend sstart send evalue bitscore'"
    os.system(cmd)

def process_blast_out():
    inf = open(tempname+".rawblastn","r")
    clus = set()
    for i in inf:
        spls = i.strip().split("\t")
        #get this test from internal_conf
        if min(float(spls[1]),float(spls[3]))/max(float(spls[1]),float(spls[3])) < length_limit:
            continue
        if (max(float(spls[10]),float(spls[11]))-min(float(spls[10]),float(spls[11]))) / float(spls[1]) < length_limit:
            continue
        if (max(float(spls[12]),float(spls[13]))-min(float(spls[12]),float(spls[13]))) / float(spls[3]) < length_limit:
            continue
        if float(spls[14]) != 0:
            if -math.log10(float(spls[14])) < -math.log(evalue_limit):
                continue
        clus.add(spls[2].split("___")[0])
    inf.close()
    return clus

def add_file(fromfile,tofile):
    tf = open(tofile,"a")
    ff = open(fromfile,"r")
    for i in ff:
        tf.write(i)
    ff.close()
    tf.close()

def write_merge_table_and_temp_aln_file(filelist):
    tf = open("subMSAtable","w")
    tf2 = open("temp.mergealn","w")
    count = 1
    addlater = []
    for i in filelist:
        flcount = 0
        for j in seq.read_fasta_file_iter(i):
            flcount += 1
        if flcount > 1:
            for j in seq.read_fasta_file_iter(i):
                tf.write(str(count)+" ")
                count += 1
                tf2.write(j.get_fasta())
            tf.write("# "+i)
            tf.write("\n")
        else:
            for j in seq.read_fasta_file_iter(i):
                addlater.append(j.get_fasta())
    for i in addlater:
        tf2.write(i)
    tf.close()
    tf2.close()
    #x = [j.split("/")[-1] for j in filelist]
    #copyfile("subMSAtable","subMSAtable_"+".".join(x))
    #copyfile("temp.mergealn","temp.mergealn_"+".".join(x))

def check_unaligned(infile):
    clen = None
    count = 0
    for i in seq.read_fasta_file_iter(infile):
        count += 1
        if clen == None:
            clen = len(i.seq)
        else:
            if len(i.seq) != clen:
                return False
    if count == 0:
        return False
    return True

def merge_alignments(outfile):
    cmd = "mafft --thread "+nthread+" --quiet --adjustdirection --merge subMSAtable temp.mergealn 2>mafft.out > "+outfile
    os.system(cmd)
    #for some buggy reason these can be unaligned, so realigning here
    if check_unaligned(outfile) == False:
        print colored.red("PROBLEM REDOING ALIGNMENT"+" "+emoticons.get_ran_emot("sad"))

        #log.w("PROBLEM REDOING ALIGNMENT")
        copyfile("subMSAtable","problem_subMSAtable")
        copyfile("temp.mergealn","problem_temp.mergealn")
        cmd = "mafft --quiet --adjustdirection temp.mergealn > "+outfile
        os.system(cmd)
    if mac == False:
        os.system("sed -i 's/_R_//g' "+outfile)
    else:
        os.system("sed -i '' 's/_R_//g' "+outfile)
    #os.remove("subMSAtable")
    #os.remove("temp.mergealn")



if __name__ == "__main__":
    if len(sys.argv) != 3 and len(sys.argv) != 4:
        print "python "+sys.argv[0]+" fromclusterdir tooutdir [logfile]"
        sys.exit(0)
    dir1 = sys.argv[1]
    diro = sys.argv[2]
    logfile = "pyphlawd.log"
    if len(sys.argv) == 4:
        logfile = sys.argv[3]
    log = Logger(logfile)
    log.a()
    curcount = 0
    if len(os.listdir(diro)) == 0:
        from shutil import copyfile
        for i in os.listdir(dir1):
            log.w(" ".join(["INITIAL CLUSTER POPULATION COPY TO",diro+"/"+i,"FROM",dir1+"/"+i]))
            copyfile(dir1+"/"+i,diro+"/"+i)
    else:
        for i in os.listdir(diro):
            if ".fa" not in i:
                continue
            x = int(i.replace("cluster","").replace(".fa",""))
            if x > curcount:
                curcount = x
        curcount += 1
        #make blast dir of the out
        if dosamp:
            make_blast_db_from_cluster_samp(diro)
        else:
            make_blast_db_from_cluster(diro)
        count = 1
        G = nx.Graph()
        for i in os.listdir(dir1):
            if i[-3:] != ".fa":
                continue
            # doing just the sample for speed
            if dosamp:
                if os.path.isfile(dir1+"/"+i.replace(".fa",".samp")):
                    blast_file_against_db(dir1,i.replace(".fa",".samp"))
                else:
                    blast_file_against_db(dir1,i)
            else:
                blast_file_against_db(dir1,i)
            clus = process_blast_out()
            if len(clus) > 0:
                for j in clus:
                    G.add_edge(dir1+"/"+i,diro+"/"+j)
            else:
                G.add_node(dir1+"/"+i)
        # need to log these operations
        origcurcount = curcount
        for i in nx.connected_components(G):
            tf = open(diro+"/"+"cluster"+str(curcount)+".fa","w")
            log.w(" ".join(["MERGING FASTA TO",diro+"/cluster"+str(curcount)+".fa","FROM"," ".join(list(i))]))
            curcount += 1
            for j in i:
                for k in seq.read_fasta_file_iter(j):
                    tf.write(k.get_fasta())
            tf.close()
        if use_merge == True:
            for i in nx.connected_components(G):
                if len(i) > 1:
                    x = [j.replace(".fa",".aln") for j in i]
                    log.w(" ".join(["MERGING ALIGNMENTS FROM"," ".join(x)]))
                    write_merge_table_and_temp_aln_file(x)
                    outfile = diro+"/"+"cluster"+str(origcurcount)+".aln"
                    merge_alignments(outfile)
                    log.w(" ".join(["CREATED FROM MERGE",diro+"/cluster"+str(origcurcount)+".aln"]))
                    for j in i:
                        if diro in j:
                            log.w(" ".join(["REMOVING ALIGNMENTS",j,j.replace(".fa",".aln")]))
                            os.remove(j)
                            os.remove(j.replace(".fa",".aln"))
                            if os.path.isfile(j.replace(".fa",".tre")):
                                os.remove(j.replace(".fa",".tre"))
                            if os.path.isfile(j.replace(".fa",".samp")):
                                os.remove(j.replace(".fa",".samp"))

                else:
                    tf = open(diro+"/"+"cluster"+str(origcurcount)+".aln","w")
                    for j in i:
                        #copyfile(j,diro+"/cluster"+str(origcurcount)+".fa")
                        log.w(" ".join(["CREATING SINGLE ALIGNMENT",diro+"/cluster"+str(origcurcount)+".aln","FROM",j.replace(".fa",".aln")]))
                        numseq = 0
                        for k in seq.read_fasta_file_iter(j.replace(".fa",".aln")):
                            tf.write(k.get_fasta())
                            numseq += 1
                        if diro in j:
                            log.w(" ".join(["REMOVING ALIGNMENTS"+j,j.replace(".fa",".aln")]))
                            os.remove(j)
                            os.remove(j.replace(".fa",".aln"))
                            if os.path.isfile(j.replace(".fa",".tre")):
                                os.remove(j.replace(".fa",".tre"))
                            if os.path.isfile(j.replace(".fa",".samp")):
                                os.remove(j.replace(".fa",".samp"))
                    tf.close()
                origcurcount += 1
    log.c()
