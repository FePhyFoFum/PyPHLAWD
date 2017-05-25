import sys,os,sqlite3

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "python "+sys.argv[0]+" DB outfile"
        sys.exit()
    DB = sys.argv[1]
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    outf = open(sys.argv[2],"w")
    c.execute("select ncbi_id,name from taxonomy;")
    l = c.fetchall()
    for j in l:
        outf.write(str(j[0])+"\t"+str(j[1])+"\n")
    outf.close()

