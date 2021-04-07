import argparse
import sys
import os
import os.path
import ftplib
import gzip
import tarfile
import sqlite3


def create_db(DBFILE):
    conn = sqlite3.connect(DBFILE)
    c = conn.cursor()
    c.execute("create table taxonomy (id INTEGER PRIMARY KEY,ncbi_id INTEGER,name VARCHAR(255),name_class VARCHAR(32),node_rank VARCHAR(32),parent_ncbi_id INTEGER,edited_name VARCHAR(255),left_value INTEGER,right_value INTEGER);" );
    c.execute("CREATE INDEX taxonomy_left_value on taxonomy(left_value);");
    c.execute("CREATE INDEX taxonomy_name on taxonomy(name);");
    c.execute("CREATE INDEX taxonomy_ncbi_id on taxonomy(ncbi_id);");
    c.execute("CREATE INDEX taxonomy_parent_ncbi_id on taxonomy(parent_ncbi_id);");
    c.execute("CREATE INDEX taxonomy_right_value on taxonomy(right_value);");
    c.execute("CREATE INDEX taxonomy_edited_name on taxonomy(edited_name);");

    c.execute("create table sequence (id INTEGER PRIMARY KEY,ncbi_id INTEGER,locus VARCHAR(128), accession_id VARCHAR(128), description TEXT, seqfile LONGTEXT);");
    c.execute("CREATE INDEX sequence_ncbi_id on sequence(ncbi_id);");
    c.execute("CREATE INDEX sequence_accession_id on sequence(accession_id);");
    #c.execute("CREATE INDEX sequence_version_id on sequence(version_id);");

    c.execute("create table information (id INTEGER PRIMARY KEY, name VARCHAR(128), value VARCHAR(128));");
    c.execute("create table files (id INTEGER PRIMARY KEY, filename VARCHAR(255));")
    conn.close()


def create_name(st):
    st = st.replace('"','').replace("'",'')
    return st

def create_edited_name(st):
    return st

"""
citations.dmp         merged.dmp            
delnodes.dmp          gc.prt                
names.dmp             readme.txt
division.dmp          gencode.dmp           
nodes.dmp
"""
def read_tax_file(filename,db):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    rank = {}
    parent_id = {}
    tar = tarfile.open(filename)
    tar.extractall()
    tar.close()
    f = open("nodes.dmp","r")
    for i in f:
        s = [st.strip() for st in i.strip().split("|")]
        ncbi_id = s[0]
        rank[ncbi_id] = s[2]
        parent_id[ncbi_id] = s[1]
    f.close()

    f = open("names.dmp","r")
    count = 0
    for i in f:
        s = [st.strip() for st in i.strip().split("|")]
        if count % 100000 == 0:
            print(count)
        gin = s[0]
        try:
            rank[gin]
        except:
            continue
        nm = create_name(s[1])
        nm_class = s[3]
        ednm = create_edited_name(nm)
        sql = "insert into taxonomy (ncbi_id,name,name_class,node_rank,parent_ncbi_id,edited_name) values ("
        sql += gin+",\""
        sql += nm+"\",'";
        sql += nm_class+"','"
        sql += rank[gin]+"',";
        sql += parent_id[gin]+",'"
        sql += ednm+"');"
        c.execute(sql)
        count += 1
    f.close()
    conn.commit()
    conn.close()
    files = ['citations.dmp','merged.dmp','delnodes.dmp','gc.prt','names.dmp','readme.txt','division.dmp','gencode.dmp','nodes.dmp']
    for i in files:
        os.remove(i)

def read_gb_flat_file(filename,db,storeseqs=False,maxsize=None):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    fl = gzip.open (filename,"r")
    new = False
    locus = None
    title = None
    defi = None
    taxonid = None
    length = 0
    descr = False
    seq = None
    seqst = False
    count =0
    added = 0
    for i in fl:
        i = str(i.decode())#or decode
        if descr == True:
            if "ACCESSION" in i:
                descr = False
            else:
                defi += " "+i.strip()
        if seqst == True:
            if "//" == i[0:2]:
                new = False
                if maxsize != None:
                    if len(seq) > maxsize:
                        continue
                if storeseqs and length != len(seq):
                    print(length,len(seq))
                    sys.exit(0)
                sql = "insert into sequence (ncbi_id,locus,accession_id,description,seqfile) values ("
                sql += taxonid+",'"
                sql += locus+"','"
                sql += locus+"','"
                #sql += locus+"','";
                sql += defi.replace("'","") +"','"
                sql += filename.split("/")[-1]
                #sql += title +"','";
                sql += "')"
                added += 1
                try:
                    c.execute(sql)
                except:
                    print(sql)
                    sys.exit()
                #print(taxonid,locus,defi)
            else:
                if storeseqs:
                    seq += "".join(i.strip().split()[1:])
        if "LOCUS" ==  i[0:5]:
            locus = i.strip().split()[1]
            #print(locus)
            try:
                length = int(i.strip().split()[2])
            except:
                print(i)
                sys.exit(0)
            new = True
        elif "DEFINITION" in i:
            defi = i.replace("DEFINITION  ","").strip()
            descr = True
        elif "ORIGIN" in i:
            seqst = True
            seq = ""
        elif "db_xref=" in i and "taxon" in i:
            try:
                taxonid = i.replace('"',"").strip().replace("'","").split("taxon:")[1]
            except:
                print(i)
                continue
    conn.commit()
    fl.close()
    conn.close()
    print("    added ",added,"seqs")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-d", "--dir",help="Which directory for database?",required=True)
    parser.add_argument("-o","--outdb",help="What is the output database filename",required=True)
    parser.add_argument("-s", "--seqs",help="store seqs?",default=False,required=False)
    parser.add_argument("-f", "--gzfilesdir",help="Where are the gzfiles",required=True)
    parser.add_argument("-m", "--maxsize",help="Don't keep seqs with length great than ",default=0,required=False)
    parser.add_argument("-a", "--addnew",help="Just add new files from dir",default=False)

    if len(sys.argv[1:]) == 0:
        sys.argv.append("-h")

    args = parser.parse_args()
    
    maxsize = args.maxsize
    if maxsize == 0:
        maxsize = None

    std = args.dir
    if std[-1] != "/":
        std += "/"
    
    dbn = std + args.outdb
    if args.addnew == False:
        create_db(dbn)
        GBFTP = "ftp.ncbi.nih.gov"
        ftp = ftplib.FTP(GBFTP)
        ftp.login("anonymous", "anonymous")
        ftp.cwd("pub/taxonomy/")
        tf = "taxdump.tar.gz"
        with open(std+tf,'wb') as f:
            ftp.retrbinary('RETR '+tf,f.write)
        ftp.close()
        read_tax_file(std+tf,dbn)
        os.remove(std+tf)

    fd = args.gzfilesdir
    if fd[-1] != "/":
        fd += "/"
    kf = [i for i in os.listdir(fd) if ".seq.gz" in i]
    if args.addnew:
        conn = sqlite3.connect(dbn)
        c = conn.cursor()
        x = c.execute("SELECT filename from files;")
        for i in x:
            print(i[0])
            if i[0] in kf:
                kf.remove(i[0])
        c.close()
    count = 1
    for i in kf:
        print(i,count,"of",len(kf))
        read_gb_flat_file(fd+i,dbn,args.seqs,maxsize)
        conn = sqlite3.connect(dbn)
        c = conn.cursor()
        x = c.execute("INSERT into files (filename) values ('"+i+"');")
        conn.commit()
        conn.close()
        count += 1
