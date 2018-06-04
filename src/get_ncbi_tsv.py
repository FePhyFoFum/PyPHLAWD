#!/usr/bin/python

import argparse
import sys,os,sqlite3

from get_ncbi_tax_tree import clean_name

# prints out following columns: id, pid, name, clean_name, rank

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--taxon", help="Taxon constituting root node of tree (name or id)",
                        required=True)
    parser.add_argument("-d", "--database", help="Location of database", required=True)
    parser.add_argument("-o", "--outfile", help="Output tree file", required=False)
    
    args = parser.parse_args()
    
    taxon = args.taxon
    DB = args.database
    
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("select ncbi_id,parent_ncbi_id,name,node_rank from taxonomy where name_class = 'scientific name'")
    
    # parse output
    count = 0
    pid = {} # key is the child id and the value is the parent
    cid = {} # key is the parent and value is the list of children
    nid = {}
    nrank = {}
    targetid = ""
    l = c.fetchall()
    for j in l:
        tid = str(j[0])
        parentid = str(j[1])
        name = str(j[2])
        rank = str(j[3])
        nrank[tid] = rank
        nid[tid] = name
        pid[tid] = parentid
        if tid == taxon or name == taxon:
            #print "name set: " + name + "; tid: " + str(tid)
            targetid = tid
            pid[tid] = ""
        if parentid not in cid: 
            cid[parentid] = []
        cid[parentid].append(tid)
        count += 1
    
    stack = [targetid]
    if args.outfile:
        outfile = open(args.outfile,"w")
        outfile.write("id\t|\tpid\t|\tname\t|\tclean name\t|\trank\t|\t\n")
    else:
        print "id\t|\tpid\t|\tname\t|\tclean name\t|\trank\t|\t"
    while len(stack) > 0:
        tempid = stack.pop()
        if args.outfile:
            outfile.write(tempid+"\t|\t"+pid[tempid]+"\t|\t"+nid[tempid]+"\t|\t"+clean_name(nid[tempid])+"\t|\t"+nrank[tempid]+"\t|\t\n")
        else:
            print tempid+"\t|\t"+pid[tempid]+"\t|\t"+nid[tempid]+"\t|\t"+clean_name(nid[tempid])+"\t|\t"+nrank[tempid]+"\t|\t"
        if tempid in cid:
            for i in cid[tempid]:
                stack.append(i)
    
