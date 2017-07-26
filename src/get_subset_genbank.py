import sys,os,sqlite3
from bad_seqs import gids
from bad_taxa import taxonids
from exclude_patterns import patterns
from exclude_desc_patterns import desc_patterns
from conf import smallest_size

"""
this version of the file is updated to take into account the change from gi to acc

"""

def make_files_with_id(taxonid, DB,outfilen,outfile_tbln,remove_genomes=False, limitlist = None):
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
        #exclude bad taxa
        if str(id) in taxonids:
            continue
        c.execute("select name from taxonomy where ncbi_id = ? and name_class = 'scientific name'",(id,))
        l = c.fetchall()
        for j in l:
            tname = str(j[0])
        # exclude some patterns 
        badpattern = False
        for i in patterns:
            if i in tname:
                badpattern = True
                break
        if badpattern:
            continue
        c.execute("select * from sequence where ncbi_id = ?",(id,))
        l = c.fetchall()
        for j in l:
            #if the title sequence name is not the same as the id name (first part)
            #  then we skip it. sorry sequence! you are outta here
            try:
                if tname.split(" ")[0]+tname.split(" ")[1] != str(j[5]).split(" ")[0]+str(j[5]).split(" ")[1]:
                    continue
            except:
                continue
            #catch bad seqs
            if str(j[3]) in gids or str(j[2]) in gids:
                continue
            #bad description
            bad_desc = False
            for k in desc_patterns:
                if k in str(j[5]):
                    bad_desc = True
                    break
            if bad_desc:
                continue
            if len(str(j[7])) < smallest_size:
                continue
            if limitlist != None and str(j[1]) not in limitlist:
                continue
            if remove_genomes:
                if len(str(j[7])) > 10000:
                    outfileg.write(">"+str(j[3])+"\n")
                    outfileg.write(str(j[7])+"\n")
                else:
                    outfile.write(">"+str(j[3])+"\n")
                    outfile.write(str(j[7])+"\n")
            else:
                outfile.write(">"+str(j[3])+"\n")
                outfile.write(str(j[7])+"\n")
            outfile_tbl.write(str(j[0])+"\t"+str(j[1])+"\t"+str(j[2])+"\t"+str(j[3])+"\t"+str(tname)+"\t"+str(j[5])+"\t"+str(j[6])+"\n")
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

def make_files_with_id_internal(taxonid, DB,outfilen,outfile_tbln,remove_genomes=False, limitlist = None):
    outfile = open(outfilen,"w")
    outfileg = None
    if remove_genomes:
        outfileg = open(outfilen+".genomes","w")
    outfile_tbl = open(outfile_tbln,"w")
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    #only get the ones that are this specific taxon
    c.execute("select name from taxonomy where ncbi_id = ? and name_class = 'scientific name'",(str(taxonid),))
    l = c.fetchall()
    for j in l:
        tname = str(j[0])
    c.execute("select * from sequence where ncbi_id = ?",(str(taxonid),))
    l = c.fetchall()
    for j in l:
        #if the title sequence name is not the same as the id name (first part)
        #  then we skip it. sorry sequence! you are outta here
        try:
            if tname.split(" ")[0]+tname.split(" ")[1] != str(j[5]).split(" ")[0]+str(j[5]).split(" ")[1]:
                continue
        except:
            continue
        #catch bad seqs
        if str(j[3]) in gids or str(j[2]) in gids:
            continue
        #bad description
        bad_desc = False
        for k in desc_patterns:
            if k in str(j[5]):
                bad_desc = True
                break
        if bad_desc:
            continue
        if len(str(j[7])) < smallest_size:
            continue
        #exclude bad taxa
        if str(j[1]) in taxonids:
            continue
        badpattern = False
        for i in patterns:
            if i in tname:
                badpattern = True
                break
        if badpattern:
            continue
        if limitlist != None and str(j[1]) not in limitlist:
            continue
        if remove_genomes:
            if len(str(j[7])) > 10000:
                outfileg.write(">"+str(j[3])+"\n")
                outfileg.write(str(j[7])+"\n")
            else:
                outfile.write(">"+str(j[3])+"\n")
                outfile.write(str(j[7])+"\n")
        else:
            outfile.write(">"+str(j[3])+"\n")
            outfile.write(str(j[7])+"\n")
    # get the children of the taxon that have no children (and so the sequences would go here)
    keepers = []
    c.execute("select ncbi_id from taxonomy where parent_ncbi_id = ?",(str(taxonid),))
    l = c.fetchall()
    for j in l:
        nt = str(j[0])
        c.execute("select ncbi_id from taxonomy where parent_ncbi_id = ?",(str(nt),))
        m = c.fetchall()
        count = 0
        for n in m:
            count += 1
        if count == 0:
            keepers.append(nt)
    #get everything else for the table
    species = []
    stack = []
    stack.append(str(taxonid))
    while len(stack) > 0:
        id = stack.pop()
        if id in species:
            continue
        else:
            species.append(id)
        #exclude bad taxa
        if str(id) in taxonids:
            continue
        c.execute("select name from taxonomy where ncbi_id = ? and name_class = 'scientific name'",(id,))
        l = c.fetchall()
        for j in l:
            tname = str(j[0])
        # exclude some patterns 
        badpattern = False
        for i in patterns:
            if i in tname:
                badpattern = True
                break
        if badpattern:
            continue
        c.execute("select * from sequence where ncbi_id = ?",(id,))
        l = c.fetchall()
        #only record everything for the table
        for j in l:
            #if the title sequence name is not the same as the id name (first part)
            #  then we skip it. sorry sequence! you are outta here
            try:
                if tname.split(" ")[0]+tname.split(" ")[1] != str(j[5]).split(" ")[0]+str(j[5]).split(" ")[1]:
                    continue
            except:
                continue
            #catch bad seqs
            if str(j[3]) in gids or str(j[2]) in gids:
                continue
            if limitlist != None and str(j[1]) not in limitlist:
                continue
            if str(j[1]) in keepers:
                if len(str(j[7])) > 10000:
                    outfileg.write(">"+str(j[3])+"\n")
                    outfileg.write(str(j[7])+"\n")
                else:
                    outfile.write(">"+str(j[3])+"\n")
                    outfile.write(str(j[7])+"\n")
            outfile_tbl.write(str(j[0])+"\t"+str(j[1])+"\t"+str(j[2])+"\t"+str(j[3])+"\t"+str(tname)+"\t"+str(j[5])+"\t"+str(j[6])+"\n")
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
            outfile_tbl.write(str(j[0])+"\t"+str(j[1])+"\t"+str(j[2])+"\t"+str(j[3])+"\t"+str(tname)+"\t"+str(j[5])+"\t"+str(j[6])+"\n")
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
            outfile.write(str(j[7])+"\n")
            outfile_tbl.write(str(j[0])+"\t"+str(j[1])+"\t"+str(j[2])+"\t"+str(j[3])+"\t"+str(tname)+"\t"+str(j[4])+"\n")
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
