import sys
import os
import tree_reader
import emoticons
from clint.textui import colored

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("python "+sys.argv[0]+" in.tre location")
        sys.exit(0)

    tree = next(tree_reader.read_tree_file_iter(sys.argv[1]))
    dirl = sys.argv[2]+"/"

    didntmake = set()

    for i in tree.iternodes(order="PREORDER"):
        if "unclassified" in i.label:
            didntmake.add(i)
            continue
        if "environmental" in i.label:
            didntmake.add(i)
            continue
        if i.parent in didntmake:
            didntmake.add(i)
            continue
        if i != tree:
            i.label = i.parent.label+"/"+i.label
        try:
            os.mkdir(dirl+i.label)
        except:
            print(colored.red("PROBLEM CREATING"),dirl+i.label,colored.red(emoticons.get_ran_emot("sad")))
            sys.exit(1)
        try:
            os.mkdir(dirl+i.label+"/clusters")
        except:
            print(colored.red("PROBLEM CREATING"),dirl+i.label+"/clusters",colored.red(emoticons.get_ran_emot("sad")))
            sys.exit(1)
    
