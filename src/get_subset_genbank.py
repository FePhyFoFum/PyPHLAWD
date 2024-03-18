import sys,os,sqlite3
import gzip
from bad_seqs import gids
from bad_taxa import taxonids
from exclude_patterns import patterns
from exclude_desc_patterns import desc_patterns
from conf import smallest_size
from conf import filternamemismatch

"""
this version of the file is updated to take into account the change from gi to acc

"""

def get_seq_from_gz(gzdir, filename, idtoget):
    fl = gzip.open(gzdir+"/"+filename,"r")
    for i in fl:
        if str(i.decode()).split(" ")[0] == idtoget:
            return str(i.decode()).split(" ")[1]
    fl.close()
    return None

def get_seqs_from_gz(gzdir, filename, idstoget):
    fl = gzip.open(gzdir+"/"+filename,"r")
    idtoseq = {}
    for i in idstoget:
        idtoseq[i] = None
    idstoget = set(idstoget)
    for i in fl:
        if str(i.decode()).split(" ")[0] in idstoget:
            idtoseq[str(i.decode()).split(" ")[0]]= str(i.decode()).split(" ")[1]
    fl.close()
    return idtoseq

# if outfilen and outfile_tbln are None, the results will be returned
def make_files_with_id(taxonid, DB,outfilen,outfile_tbln, gzfileloc,
    remove_genomes=False, limitlist = None,excludetax = None):
    if outfilen != None and outfile_tbln != None:
        outfile = open(outfilen,"w")
        outfileg = None
        if remove_genomes:
            outfileg = open(outfilen+".genomes","w")
        outfile_tbl = open(outfile_tbln,"w")
    retseqs = [] # return if filenames aren't given
    rettbs = [] # returning if filenames aren't given
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    species = []
    stack = []
    stack.append(str(taxonid))
    files_ids = {}# key is the file, value is a list of ids
    ids_props = {}# key is id, value is list of properties
    while len(stack) > 0:
        id = stack.pop()
        if id in species:
            continue
        else:
            species.append(id)
        #exclude bad taxa
        if str(id) in taxonids:
            continue
        if excludetax != None:
            if str(id) in excludetax:
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
        c.execute("select * from sequence where ncbi_id = ?",(id,)) # this will give the filename in the folder
        l = c.fetchall()
        for j in l:
            #if the title sequence name is not the same as the id name (first part)
            #  then we skip it. sorry sequence! you are outta here
            if filternamemismatch:
                try:
                    if tname.split(" ")[0]+tname.split(" ")[1] != str(j[4]).split(" ")[0]+str(j[4]).split(" ")[1]:
                        continue
                except:
                    continue
            #catch bad seqs
            if str(j[3]) in gids or str(j[2]) in gids:
                continue
            #bad description
            bad_desc = False
            for k in desc_patterns:
                if k in str(j[4]):
                    bad_desc = True
                    break
            if bad_desc:
                continue
            # str(j[7]) is the seq but now it is the seq file
            # now str(j[5]) is the file
            tfilen = "seqs."+str(j[5])
            if tfilen not in files_ids:
                files_ids[tfilen] = []
            files_ids[tfilen].append(str(j[2]))
            ids_props[str(j[2])] = [str(j[0]),str(j[1]),str(j[2]),str(j[3]),str(tname),str(j[5])]
        c.execute("select ncbi_id from taxonomy where parent_ncbi_id = ?",(id,))
        childs = []
        l = c.fetchall()
        for j in l:
            childs.append(str(j[0]))
            stack.append(str(j[0]))
    # get all the seqs from the file at once
    for fn in files_ids:
        idstoseq = get_seqs_from_gz(gzfileloc,fn,files_ids[fn])
        for tid in idstoseq:
            seqstr = idstoseq[tid]
            if seqstr == None: # too big
                continue
            if len(seqstr) < smallest_size:
                continue
            #exclude bad taxa
            if ids_props[tid][1] in taxonids:
                continue
            badpattern = False
            #MAKE SURE THIS IS OK TODO THIS SHOULD BE DONE ABOVE
            #for i in patterns:
            #    if i in tname:
            #        badpattern = True
            #        break
            #if badpattern:
            #    continue
            if limitlist != None and ids_props[tid][1] not in limitlist:
                continue
            # we are writing
            seqst = ">"+str(ids_props[tid][3]+"\n"+seqstr)
            tblst = "\t".join(ids_props[tid])
            if outfilen != None and outfile_tbln != None:
                if remove_genomes:
                    if len(seqstr) > 10000:
                        outfileg.write(seqst+"\n")
                    else:
                        outfile.write(seqst+"\n")
                else:
                    outfile.write(seqst+"\n")
                outfile_tbl.write(tblst+"\n")
            # we are returning
            else:
                if len(seqstr) < 10000:
                    retseqs.append(seqst)
                    rettbs.append(tblst)
    # we are writing
    if outfilen != None and outfile_tbln != None:
        outfile.close()
        if remove_genomes:
            outfileg.close()
        outfile_tbl.close()
    # we are returning
    else:
        return retseqs,rettbs

# if outfilen and outfile_tbln are None, the results will be returned
def make_files_with_id_internal(taxonid, DB,outfilen,outfile_tbln,gzfileloc,
    remove_genomes=False, limitlist = None):
    if outfilen != None and outfile_tbln != None:
        outfile = open(outfilen,"w")
        outfileg = None
        if remove_genomes:
            outfileg = open(outfilen+".genomes","w")
        outfile_tbl = open(outfile_tbln,"w")
    retseqs = [] # return if filenames aren't given
    rettbs = [] # returning if filenames aren't given
    files_ids = {}# key is the file, value is a list of ids
    ids_props = {}# key is id, value is list of properties
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
        if filternamemismatch:
            try:
                if tname.split(" ")[0]+tname.split(" ")[1] != str(j[4]).split(" ")[0]+str(j[4]).split(" ")[1]:
                    continue
            except:
                continue
        #catch bad seqs
        if str(j[3]) in gids or str(j[2]) in gids:
            continue
        #bad description
        bad_desc = False
        for k in desc_patterns:
            if k in str(j[4]):
                bad_desc = True
                break
        if bad_desc:
            continue
        # now str(j[5]) is the file
        tfilen = "seqs."+str(j[5])
        if tfilen not in files_ids:
            files_ids[tfilen] = []
        files_ids[tfilen].append(str(j[2]))
        ids_props[str(j[2])] = [str(j[0]),str(j[1]),str(j[2]),str(j[3]),str(tname),str(j[5])]
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
            if filternamemismatch:
                try:
                    if tname.split(" ")[0]+tname.split(" ")[1] != str(j[4]).split(" ")[0]+str(j[4]).split(" ")[1]:
                        continue
                except:
                    continue
            #catch bad seqs
            if str(j[3]) in gids or str(j[2]) in gids:
                continue
            if limitlist != None and str(j[1]) not in limitlist:
                continue
            tfilen = "seqs."+str(j[5])
            if tfilen not in files_ids:
                files_ids[tfilen] = []
            if str(j[1]) in keepers:
                files_ids[tfilen].append(str(j[2]))
            ids_props[str(j[2])] = [str(j[0]),str(j[1]),str(j[2]),str(j[3]),str(tname),str(j[5])]
            tblst = "\t".join(ids_props[str(j[2])])
            outfile_tbl.write(tblst+"\n")
        c.execute("select ncbi_id from taxonomy where parent_ncbi_id = ?",(id,))
        childs = []
        l = c.fetchall()
        for j in l:
            childs.append(str(j[0]))
            stack.append(str(j[0]))
    for fn in files_ids:
        idstoseq = get_seqs_from_gz(gzfileloc,fn,files_ids[fn])
        for tid in idstoseq:
            seqstr = idstoseq[tid]
            if seqstr == None: # too big
                continue
            if len(seqstr) < smallest_size:
                continue
            #exclude bad taxa
            if ids_props[tid][1] in taxonids:
                continue
            #MAKE SURE THIS IS OK TODO
            #badpattern = False
            #for i in patterns:
            #    if i in tname:
            #        badpattern = True
            #        break
            #if badpattern:
            #    continue
            if limitlist != None and ids_props[tid][1] not in limitlist:
                continue
            # we are writing
            seqst = ">"+str(ids_props[tid][3]+"\n"+seqstr)
            tblst = "\t".join(ids_props[tid])
            if outfilen != None and outfile_tbln != None:
#                if ids_props[tid][1] in keepers:
                if remove_genomes:
                    if len(seqstr) > 10000:
                        outfileg.write(seqst+"\n")
                    else:
                        outfile.write(seqst+"\n")
                else:
                    outfile.write(seqst+"\n")
                #outfile_tbl.write(tblst+"\n")
            # we are returning
            else:
                if len(seqstr) < 10000:
                    retseqs.append(seqst)
                    rettbs.append(tblst)
    # we are writing
    if outfilen != None and outfile_tbln != None:
        outfile.close()
        if remove_genomes:
            outfileg.close()
        outfile_tbl.close()
    # we are returning
    else:
        return retseqs,rettbs

# if you send outfile_tbln as None, it will return the results
def make_files_with_id_justtable(taxonid, DB,outfile_tbln):
    if outfile_tbln != None:
        outfile_tbl = open(outfile_tbln,"w")
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    species = []
    stack = []
    tbl = []
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
            tbls = str(j[0])+"\t"+str(j[1])+"\t"+str(j[2])+"\t"+str(j[3])+"\t"+str(tname)+"\t"+str(j[5])+"\t"+str(j[6])
            if outfile_tbln != None:
                outfile_tbl.write(tbls+"\n")
            else:
                tbl.append(tbls)
        c.execute("select ncbi_id from taxonomy where parent_ncbi_id = ?",(id,))
        childs = []
        l = c.fetchall()
        for j in l:
            childs.append(str(j[0]))
            stack.append(str(j[0]))
    if outfile_tbln != None:
        outfile_tbl.close()
    else:
        return tbl

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
        print("usage: python "+sys.argv[0]+" tid db outfile")
        sys.exit(0)
    tid = sys.argv[1]
    DB = sys.argv[2]
    outfilen = sys.argv[3]
    outfile_tbln = sys.argv[3]+".table"
    make_files_with_id(tid, DB,outfilen,outfile_tbln)
