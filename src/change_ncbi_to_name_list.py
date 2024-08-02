import sys
import sqlite3
import argparse as ap


def generate_argparser():
    parser = ap.ArgumentParser(prog="change_ncbi_to_name_tre.py",
        formatter_class=ap.ArgumentDefaultsHelpFormatter)
    parser = ap.ArgumentParser()
    parser.add_argument("-d", "--db", type=str, help="NCBI database", required=True)
    parser.add_argument("-i", "--infile", type=str, help="Input list", required=True)
    parser.add_argument("-o", "--outfile", type=str, help="Output list", required=True)
    return parser

if __name__ == "__main__":
    parser = generate_argparser()
    if len(sys.argv[1:]) == 0:
        sys.argv.append("-h")
    args = parser.parse_args(sys.argv[1:])
    
    conn = sqlite3.connect(args.db)
    c = conn.cursor()
    of = open(args.infile,"r")
    oof = open(args.outfile,"w")
    for i in of:
        i = i.strip()
        c.execute("select name_class,edited_name,left_value,right_value from taxonomy where ncbi_id = ?", (i, ))
        nm = ""
        lf = ""
        rt = ""
        for k in c:
            if str(k[0]) == "scientific name":
                nm = str(k[1])
                lf = str(k[2])
                rt = str(k[3])
        c.execute("select edited_name from taxonomy where name_class = ? and left_value < ? and right_value > ? and node_rank = ?",("scientific name",lf,rt,"family"))
        fam = ""
        ft = c.fetchone()
        if len(ft) > 0:
            fam = ft[0]
        #for k in c:
        #    print(k)
        oof.write(fam+"\t"+nm+"\n")
    of.close()
    oof.close()
