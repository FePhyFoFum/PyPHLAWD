import tree_reader,os,sys

# using rooted trees for unrooted means ignoring anything with one
def calc_biparts(tree1):
    allbiparts1 = []
    allbiparts2 = []
    for i in tree1.iternodes():
        bp1, bp2 = get_bipart(i, tree1)
        if len(bp1) < 2 or len(bp2) < 2:
            continue
        if bp1 in allbiparts1 or bp1 in allbiparts2:
            continue
        allbiparts1.append(bp1)
        allbiparts2.append(bp2)
    return allbiparts1, allbiparts2


def get_bipart(node, root):
    rtlvs = []
    for i in root.leaves_fancy():
        rtlvs.append(i.label)
    ndlvs = []
    for i in node.leaves_fancy():
        ndlvs.append(i.label)
    bp1 = set(rtlvs) - set(ndlvs)
    bp2 = set(ndlvs)
    return bp1, bp2


def get_name(label):
    """Get taxonID from a tip label or a file name
    same = {"FZQN":"Sila","Sivu_ALN":"Sivu",\
            "DVXD":"EGOS","JGAB":"Mija",\
            "AmhyPAC":"Amhy","SaeuGB":"Saeu",\
            "Pomi2":"Pomi","WQUF":"NepSFB",\
            "GIWN":"MJM1773","OMYK":"Trpo",\
            "EZGR":"Pool","ZBTA":"Boco"}"""
    same = {}
    # store names that confirmed to belong to the same species and can be merged
    if "@" in label:name = label.split("@")[0]
    elif "." in label: name = label.split(".")[0]
    else: name = label
    if name in same: return same[name]
    return name
    
def get_clusterID(filename):
    return filename.split(".")[0]

def get_front_labels(node):
    """given a node, return a list of front tip labels"""
    leaves = node.leaves()
    return [i.label for i in leaves]

def get_back_labels(node,root):
    """given a node, return a list of back tip labels"""
    all_labels = get_front_labels(root)
    front_labels = get_front_labels(node)
    return set(all_labels) - set(front_labels)
    
def get_front_names(node):
    """given a node, return a list of front tip taxonIDs
    list may contain identical taxonIDs"""
    labels = get_front_labels(node)
    return [get_name(i) for i in labels]

def get_back_names(node,root):
    """given a node, return a list of back tip taxonIDs
    list may contain identical taxonIDs"""
    back_labels = get_back_labels(node,root)
    return [get_name(i) for i in back_labels]

def remove_kink(node,curroot):
    """
    smooth the kink created by prunning
    to prevent creating orphaned tips
    after prunning twice at the same node
    """
    if node == curroot: #and len(curroot.children) == 2:
        #move the root away to an adjacent none-tip
        if curroot.children[0].istip: #the other child is not tip
            curroot = reroot(curroot,curroot.children[1])
        else: curroot = reroot(curroot,curroot.children[0])
    #---node---< all nodes should have one child only now
    length = node.length + (node.children[0]).length
    par = node.parent
    kink = node
    node = node.children[0]
    #parent--kink---node<
    par.remove_child(kink)
    par.add_child(node)
    node.length = length
    return node,curroot

def pass_boot_filter(node,min_ave_boot):
    """check whether the average bootstrap value pass a cutoff"""
    total = 0.0
    count = 0
    for i in node.iternodes():
        if not i.istip and i.parent != None:
            total += float(i.label)
            count += 1
    if count == 0: #extracted clades with only two tips
        return True
    boot_average = total / float(count)
    print boot_average
    return boot_average >= float(min_ave_boot)

def get_ortho_from_rooted_inclade(inclade):
    """
    input a rooted tree
    cut appart bifucating nodes when duplicated taxonIDs are detected
    """
    assert inclade.nchildren == 2, "input clade not properly rooted"
    orthologs = [] #store ortho clades
    clades = [inclade]
    while True:
        newclades = [] #keep track of subclades generated in this round
        for clade in clades:
            num_taxa = len(set(get_front_names(clade)))
            num_tips = len((get_front_labels(clade)))
            if num_taxa == num_tips: #no taxon repeats
                orthologs.append(clade)
            else: #has duplicated taxa
                for node in clade.iternodes(order=0): #PREORDER, root to tip
                    if node.istip: continue
                    assert node.nchildren >= 2, "node has less than 2 children"
                    #traverse the tree from root to tip
                    child0,child1 = node.children[0],node.children[1]
                    name_set0 = set(get_front_names(child0))
                    name_set1 = set(get_front_names(child1))
                    if len(name_set0.intersection(name_set1)) > 0:
                        if node == clade:
                            newclades += [child0,child1] #break by bifid at the base
                            child0.parent = None
                            child1.parent = None
                        elif len(name_set0) > len(name_set1): #remove child1
                            node.remove_child(child1)
                            child1.prune()
                            newclades.append(child1)
                            node,clade = remove_kink(node,clade) #no rerooting here
                            newclades.append(clade)
                        else: #remove child0
                            node.remove_child(child0)
                            child0.prune()
                            newclades.append(child0)
                            node,clade = remove_kink(node,clade) #no rerooting here
                            newclades.append(clade)
                        break
        if newclades == []: break
        clades = newclades
    return orthologs

def extract_rooted_ingroup_clades(root,ingroups,outgroups,min_ingroup_taxa):
    """
    input a tree with ingroups and at least 1 outgroups
    output a list of rooted ingroup clades
    """
    inclades = []
    while True:
        max_score,direction,max_node = 0,"",None
        for node in root.iternodes():
            front,back = 0,0
            front_names_set = set(get_front_names(node))
            for name in front_names_set:
                if name in outgroups:
                    front = -1
                    break
                elif name in ingroups: front += 1
                else: sys.exit("Check taxonID "+name)
            back_names_set = set(get_back_names(node,root))
            for name in back_names_set:
                if name in outgroups:
                    back = -1
                    break
                elif name in ingroups: back += 1
                else: sys.exit("Check taxonID "+name)
            if front > max_score:
                max_score,direction,max_node = front,"front",node
            if back > max_score:
                max_score,direction,max_node = back,"back",node
        #print max_score,direction
        if max_score >= min_ingroup_taxa:
            if direction == "front":
                inclades.append(max_node)
                kink = max_node.prune()
                if len(root.leaves()) > 3:
                    newnode,root = remove_kink(kink,root)
                else: break
            elif direction == "back":
                par = max_node.parent
                par.remove_child(max_node)
                max_node.prune()
                inclades.append(reroot(root,par))#flip dirction
                if len(max_node.leaves()) > 3:
                    max_node,root = remove_kink(max_node,max_node)
                else: break
        else: break
    return inclades

def reroot(oldroot, newroot):
    oldroot.isroot = False
    newroot.isroot = True
    v = [] #path to the root
    n = newroot
    while 1:
        v.append(n)
        if not n.parent: break
        n = n.parent
    #print [ x.label for x in v ]
    v.reverse()
    for i, cp in enumerate(v[:-1]):
        node = v[i+1]
        # node is current node; cp is current parent
        #print node.label, cp.label
        cp.remove_child(node)
        node.add_child(cp)
        cp.length = node.length
        cp.label = node.label
    return newroot


def get_mrca_wnms(names,tree):
    nds = []
    for i in tree.leaves():
        if i.label in names:
            nds.append(i)
    return get_mrca(nds,tree)

def get_mrca(nodes,tree):
    traceback = []
    first = nodes[0]
    while first != tree:
        first = first.parent
        traceback.append(first)
        if first.parent == None:
            break
    curmrca = nodes[0].parent
    for i in nodes:
        if i == nodes[0]:
            continue
        curmrca = mrca_recurs(curmrca,traceback,i)
    return curmrca

def mrca_recurs(node1,path1,node2):
    path = path1[path1.index(node1):]
    parent = node2
    mrca = None
    while parent != None:
        if parent in path:
            mrca = parent
            break
        parent = parent.parent
    return mrca

#assumes an ultrametric tree
def scale_root(tree,age):
    set_heights(tree)
    oldroot = tree.height
    tree.height = age
    for i in tree.iternodes(order="postorder"):
        if i != tree and len(i.children) > 0:
            i.height = (i.height/oldroot) * tree.height
    for i in tree.iternodes(order="postorder"):
        if len(i.children) > 0:
            for j in i.children:
                j.length = i.height - j.height

def scale_edges(tree,age):
    set_heights(tree)
    oldroot = tree.height
    tree.height = age
    for i in tree.iternodes(order="postorder"):
        i.length = age/oldroot * i.length

def set_heights(tree):
    for i in tree.leaves():
        cur = i
        h = 0
        going = True
        while going:
            h += cur.length
            cur = cur.parent
            if cur == None:
                going = False
                break
            else:
                if h > cur.height:
                    cur.height = h
    for i in tree.iternodes("preorder"):
        if i != tree:
            i.height = abs(round(i.parent.height - i.length,5)) #weird rounding thing on some machines
        else:
            i.height = i.height+i.length
