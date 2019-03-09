import sys
import tree_reader

"""
this is going to remove one degree nodes
"""

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("python "+sys.argv[0]+" infile.tre outfile.tre")
        sys.exit(0)
    tree = next(tree_reader.read_tree_file_iter(sys.argv[1]))
    going = True
    while going:
        going = False
        for i in tree.iternodes():
            if len(i.children) == 1:
                sys.stderr.write("knuckle found")
                going = True
                ch = i.children[0]
                ch.length = ch.length+i.length
                par = i.parent
                par.remove_child(i)
                par.add_child(ch)
                break
    of = open(sys.argv[2],"w")
    of.write(tree.get_newick_repr(True)+";\n")
    of.close()
    
