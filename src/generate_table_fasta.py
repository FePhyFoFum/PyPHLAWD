import sys,os,sqlite3
import seq

def make_table_from_fasta(DB, fastafile, outfilen):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    outfile=open(outfilen,"w")
    for x in seq.read_fasta_file_iter(fastafile):
        sid = x.name
        c.execute("select * from sequence where accession_id = ?",(sid,))
        l = c.fetchall()
        j0,j1,j2,j3,j4,tname = "","","","","",""
        for j in l:
            j0 = str(j[0])
            j1 = str(j[1])
            j2 = str(j[2])
            j3 = str(j[3])
            j4 = str(j[4])
        c.execute("select name from taxonomy where ncbi_id = ? and name_class = 'scientific name'",(j1,))
        l = c.fetchall()
        for j in l:
            tname = str(j[0])
        outfile.write(j0+"\t"+j1+"\t"+j2+"\t"+j3+"\t"+str(tname)+"\t"+j4+"\n")
    outfile.close()

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("usage: python "+sys.argv[0]+" db fasta outfile")
        sys.exit(0)
    DB = sys.argv[1]
    inf = sys.argv[2]
    outfilen = sys.argv[3]
    make_table_from_fasta(DB,inf,outfilen)
