import sys,os,sqlite3
from bad_seqs import gids

def make_files_with_id(taxonid, DB,outfilen,outfile_tbln,remove_genomes=False):
    outfile = open(outfilen,"w")
    outfileg = None
    if remove_genomes:
        outfileg = open(outfilen+".genomes","w")
    outfile_tbl = open(outfile_tbln,"w")
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    species = []
    stack = []
    stack.append(str(taxonid))
    while len(stack) > 0:
        id = stack.pop()
        if id in species:
            continue
        else:
            species.append(id)
        c.execute("select name from taxonomy where ncbi_id = ? and name_class = 'scientific name'",(id,))
        l = c.fetchall()
        for j in l:
            tname = str(j[0])
        c.execute("select * from sequence where ncbi_id = ?",(id,))
        l = c.fetchall()
        for j in l:
            #catch bad seqs
            if str(j[3]) in gids:
                continue
            if remove_genomes:
                if len(str(j[5])) > 10000:
                    outfileg.write(">"+str(j[3])+"\n")
                    outfileg.write(str(j[5])+"\n")
                else:
                    outfile.write(">"+str(j[3])+"\n")
                    outfile.write(str(j[5])+"\n")
            else:
                outfile.write(">"+str(j[3])+"\n")
                outfile.write(str(j[5])+"\n")
            outfile_tbl.write(str(j[0])+"\t"+str(j[1])+"\t"+str(j[2])+"\t"+str(j[3])+"\t"+str(tname)+"\t"+str(j[4])+"\n")
        c.execute("select ncbi_id from taxonomy where parent_ncbi_id = ?",(id,))
        childs = []
        l = c.fetchall()
        for j in l:
            childs.append(str(j[0]))
            stack.append(str(j[0]))
    outfile.close()
    if remove_genomes:
        outfileg.close()
    outfile_tbl.close()

def make_files_with_id_justtable(taxonid, DB,outfile_tbln):
    outfile_tbl = open(outfile_tbln,"w")
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    species = []
    stack = []
    stack.append(str(taxonid))
    while len(stack) > 0:
        id = stack.pop()
        if id in species:
            continue
        else:
            species.append(id)
        c.execute("select name from taxonomy where ncbi_id = ? and name_class = 'scientific name'",(id,))
        l = c.fetchall()
        for j in l:
            tname = str(j[0])
        c.execute("select * from sequence where ncbi_id = ?",(id,))
        l = c.fetchall()
        for j in l:
            outfile_tbl.write(str(j[0])+"\t"+str(j[1])+"\t"+str(j[2])+"\t"+str(j[3])+"\t"+str(tname)+"\t"+str(j[4])+"\n")
        c.execute("select ncbi_id from taxonomy where parent_ncbi_id = ?",(id,))
        childs = []
        l = c.fetchall()
        for j in l:
            childs.append(str(j[0]))
            stack.append(str(j[0]))
    outfile_tbl.close()

def make_files(taxon, DB,outfilen,outfile_tbln):
    outfile = open(outfilen,"w")
    outfile_tbl = open(outfile_tbln,"w")
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    species = []
    stack = []
    c.execute("select ncbi_id from taxonomy where name = ?",(taxon,))
    for j in c:
        stack.append(str(j[0]))
    while len(stack) > 0:
        id = stack.pop()
        if id in species:
            continue
        else:
            species.append(id)
        c.execute("select * from sequence where ncbi_id = ?",(id,))
        l = c.fetchall()
        for j in l:
            outfile.write(">"+str(j[3])+"\n")
            outfile.write(str(j[5])+"\n")
            outfile_tbl.write(str(j[0])+"\t"+str(j[1])+"\t"+str(j[2])+"\t"+str(j[3])+"\t"+str(j[4])+"\n")
        c.execute("select ncbi_id from taxonomy where parent_ncbi_id = ?",(id,))
        childs = []
        l = c.fetchall()
        for j in l:
            childs.append(str(j[0]))
            stack.append(str(j[0]))
    outfile.close()
    outfile_tbl.close()
    

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print "usage: python "+sys.argv[0]+" tid db outfile"
        sys.exit(0)
    tid = sys.argv[1]
    DB = sys.argv[2]
    outfilen = sys.argv[3]
    outfile_tbln = sys.argv[3]+".table"
    make_files_with_id(tid, DB,outfilen,outfile_tbln)
