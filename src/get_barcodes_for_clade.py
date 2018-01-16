import sys
import sqlite3

local_smallest_size = 200
local_desc_patterns = ["barcode","Barcode","BOLD"]
"""
this is primary based on get_subset_genbank
"""
def make_files_with_id(taxonid, DB,outfilen,outfilebc,outfile_tbln,outfile_bctbln,remove_genomes=False, limitlist = None):
    outfile = open(outfilen,"w")
    outfileb = open(outfilebc,"w")
    outfileg = None
    if remove_genomes:
        outfileg = open(outfilen+".genomes","w")
    outfile_tbl = open(outfile_tbln,"w")
    outfile_btbl = open(outfile_bctbln,"w")
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
            #if the title sequence name is not the same as the id name (first part)
            #  then we skip it. sorry sequence! you are outta here
            try:
                if tname.split(" ")[0]+tname.split(" ")[1] != str(j[5]).split(" ")[0]+str(j[5]).split(" ")[1]:
                    continue
            except:
                continue
            #bad description
            bar_code = False
            for k in local_desc_patterns:
                if k in str(j[5]):
                    bar_code = True
                    break
                if  k in str(j[6]):
                    bar_code = True
                    break
            if len(str(j[7])) < local_smallest_size:
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
            if bar_code == True:
                outfileb.write(">"+str(j[3])+"\n")
                outfileb.write(str(j[7])+"\n")
                outfile_btbl.write(str(j[0])+"\t"+str(j[1])+"\t"+str(j[2])+"\t"+str(j[3])+"\t"+str(tname)+"\t"+str(j[5])+"\t"+str(j[6])+"\n")
        c.execute("select ncbi_id from taxonomy where parent_ncbi_id = ?",(id,))
        childs = []
        l = c.fetchall()
        for j in l:
            childs.append(str(j[0]))
            stack.append(str(j[0]))
    outfile.close()
    outfileb.close()
    if remove_genomes:
        outfileg.close()
    outfile_tbl.close()
    outfile_btbl.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "python "+sys.argv[0]+" db clade_id"
        sys.exit()
    tid = sys.argv[2]
    DB = sys.argv[1]
    outfilen = tid+"_all_seqs.fa"
    outfilebc = tid+"_barcodes.fasta"
    outfile_tbln = tid+"_all_seqs.table"
    outfile_bctbln = tid+"_barcodes.table"
    make_files_with_id(tid, DB,outfilen,outfilebc,outfile_tbln,outfile_bctbln,remove_genomes=True)
    
