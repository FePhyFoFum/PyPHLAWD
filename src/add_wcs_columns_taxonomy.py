import sys
import sqlite3
import argparse as ap
from clint.textui import colored
import emoticons

"""
this is for adding the plants of the world checklist to the taxonomy
this is also fairly specific and probably not important for anyone else

the data are assumed to be 
ncbi_id,wcs_id,wcs_name
"""

PLANTNCBIID = 33090

def generate_argparser ():
    parser = ap.ArgumentParser(prog="add_id_column_taxonomy.py",
        formatter_class=ap.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-b", "--database", type=str, nargs=1, required=True,
        help=("Location of database."))
    parser.add_argument("-s", "--species", type=str, nargs=1, required=True,
        help=("Location of the species file."))
    parser.add_argument("-g","--genus",type=str,nargs=1, required=True,
        help=("Location of the genus file."))
    parser.add_argument("-l", "--logfile", type=str, nargs=1, required=True,
        help=("Where to write the logfile."))
    return parser

def add_column(conn):
    c = conn.cursor()
    c.execute("ALTER TABLE taxonomy ADD custom_id VARCHAR")
    conn.commit()
    c.execute("ALTER TABLE taxonomy ADD custom_name VARCHAR")
    conn.commit()
    c.execute("ALTER TABLE taxonomy ADD custom_parent_id VARCHAR")
    conn.commit()


def get_plant_left_right(conn):
    c = conn.cursor()
    sql = "SELECT left_value,right_value from taxonomy where name_class = 'scientific name' and ncbi_id = "+str(PLANTNCBIID)
    c.execute(sql)
    l = c.fetchall()
    lf = ""
    rt = ""
    for i in l:
        lf = str(i[0])
        rt = str(i[1])
    return lf,rt

def process_genera(conn,infile,lf,rt):
    c = conn.cursor()
    unmatched = []
    fl = open(infile,"r")
    for i in fl:
        spls = i.strip().split(",")
        id1 = spls[0]
        id2 = spls[1]
        sql = "SELECT ncbi_id from taxonomy where name_class = 'scientific name' and left_value >= "+str(lf)+" and right_value <= "+str(rt)+" and name = '"+str(id2)+"'"
        c.execute(sql)
        l = c.fetchall()
        nid = None
        for x in l:
            nid = str(x[0])
        if nid == None:
            # need to record these so we can add parent_ncbi_id's later
            sql = "INSERT into taxonomy (name,name_class,edited_name,custom_id,custom_name) values ('"+id2+"','scientific name','"+id2+"','"+id1+"','"+id2+"')"
            c.execute(sql)
            unmatched.append(id1)
        else:
            sql = "UPDATE taxonomy set custom_id = '"+str(id1)+"' where ncbi_id = "+nid
            c.execute(sql)
            sql = "UPDATE taxonomy set custom_name = '"+str(id2)+"' where ncbi_id = "+nid
            c.execute(sql)
    conn.commit()
    return unmatched

def add_species(conn,infile,unmatched_genera):
    c = conn.cursor()
    fl = open(infile,"r")
    for i in fl:
        spls = i.strip().split(",")
        ncbi = spls[0]
        id2 = spls[1]
        gid = spls[2]
        nm = spls[3]
        sql = "update taxonomy set custom_id = '"+str(id2)+"' where ncbi_id = "+str(ncbi)
        c.execute(sql)
        sql = "update taxonomy set custom_name = '"+str(nm)+"' where ncbi_id = "+str(ncbi)
        c.execute(sql)
        sql = "update taxonomy set custom_parent_id = '"+str(gid)+"' where ncbi_id = "+str(ncbi)
        c.execute(sql)
        # if the genus is new, then need to set the ncbi parent
        if gid in unmatched_genera:
            #if this is the case, then we need to connect the new ncbi parent of the old genus with the parent of the new custom genus
            sql = "SELECT left_value,right_value from taxonomy where name_class = 'scientific name'  and ncbi_id = "+str(ncbi)
            c.execute(sql)
            l = c.fetchall()
            for x in l:
                lf1 = str(x[0])
                rt1 = str(x[1])
            sql = "SELECT ncbi_id from taxonomy where node_rank = 'family' and name_class = 'scientific name' and left_value < "+lf1+" and right_value > "+rt1
            c.execute(sql)
            l = c.fetchall()
            for x in l:
                pn = str(x[0])
            sql = "update taxonomy set custom_parent_id = '"+pn+"' where custom_id = '"+str(gid)+"'"
            c.execute(sql)
    fl.close()
    conn.commit()


if __name__ == "__main__":
    parser = generate_argparser()
    args = parser.parse_args(sys.argv[1:])

    print(colored.blue("STARTING PYPHLAWD "+emoticons.get_ran_emot("excited")))

    dbloc = args.database[0]
    species = args.species[0]
    genus = args.genus[0]
    
    conn = sqlite3.connect(dbloc)
    lf,rt = get_plant_left_right(conn)
    add_column(conn)
    unmatched = process_genera(conn,genus,lf,rt)
    add_species(conn,species,unmatched)