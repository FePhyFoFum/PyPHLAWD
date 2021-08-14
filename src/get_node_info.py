#!/usr/bin/python

import argparse as ap
import sys,os,sqlite3

def generate_argparser():
    parser = ap.ArgumentParser()
    parser.add_argument("-t", "--taxon", help="Taxon constituting root node of clade of interest (name or id)",
                        required=True)
    parser.add_argument("-d", "--database", help="Location of database", required=True)
    parser.add_argument("-o", "--outfile", help="Output tree file", required=False)
    return parser

if __name__ == "__main__":
    parser = generate_argparser()
    if len(sys.argv[1:]) == 0:
        sys.argv.append("-h")
    
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
            #print("name set: " + name + "; tid: " + str(tid))
            targetid = tid
            pid[tid] = ""
        if parentid not in cid: 
            cid[parentid] = []
        cid[parentid].append(tid)
        count += 1
    
    if targetid == "":
        print("Error: taxon not found.")
        sys.exit(0)
    
    stack = [targetid]
    
    childcount = 0
    
    while len(stack) > 0:
        tempid = stack.pop()
        if tempid in cid:
            for i in cid[tempid]:
                stack.append(i)
        else:
            childcount +=1
    
    print("Name: " + nid[targetid] + "\nNCBI ID: " + targetid + "\nRank: " + nrank[targetid]+ "\nTerminal children: " + str(childcount))
    
