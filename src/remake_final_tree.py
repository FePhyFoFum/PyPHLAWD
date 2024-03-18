import sys
import tree_reader
import run_all_all_tips

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("python",sys.argv[0],"intre.rr intable inouttable")
        sys.exit(0)

    tblf = sys.argv[2]
    tbolf = sys.argv[3]
    og = None
    f = open(tbolf,"r")
    for j in f:
        og = j.strip().split("\t")[1]
        break
    f.close()

    #should be .rr
    tf = sys.argv[1]
    ttf = tree_reader.read_tree_file_iter(tf).__next__()
    inta = ""
    rr = ttf.children[0]
    if og in rr.lvsnms():
        rr = ttf.children[1]
    tablenms = run_all_all_tips.get_table_names(tblf)
    for j in rr.leaves():
        j.label = run_all_all_tips.clean_name(tablenms[j.label])
    ft = open(tf+".final","w")
    ft.write(rr.get_newick_repr(True)+";")
    ft.close()
