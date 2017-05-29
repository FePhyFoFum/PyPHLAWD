import sys,os,sqlite3

from get_ncbi_tax_tree_no_species import clean_name

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "python "+sys.argv[0]+" DB outfile"
        sys.exit()
    DB = sys.argv[1]
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    outf = open(sys.argv[2],"w")
    c.execute("select ncbi_id,name,edited_name from taxonomy where name_class = 'scientific name'")
    l = c.fetchall()
    for j in l:
        outf.write(str(j[0])+"\t"+str(j[1])+"\t"+str(j[2])+"\t"+clean_name(str(j[1]))+"\n")
    outf.close()

