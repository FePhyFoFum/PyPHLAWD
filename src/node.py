
class Node:
    def __init__(self):
        self.label = ""
        self.length = 0.0
        self.time_length = 0.0
        self.parent = None
        self.children = []
        self.data = {}
        self.istip = False
        self.height = 0
        self.droot = 0
        self.note = ""
    
    def add_child(self,child):
        #make sure that the child is not already in there
        assert child not in self.children
        self.children.append(child)
        child.parent = self
    
    def remove_child(self,child):
        #make sure that the child is in there
        assert child in self.children
        self.children.remove(child)
        child.parent = None
    
    def leaves(self,v=None):
        if v == None:
            v = []
        if len(self.children) == 0:
            v.append(self)
        else:
            for child in self.children:
                child.leaves(v)
        return v
    
    def get_leaf_by_name(self,nm):
        for i in self.leaves():
            if i.label == nm:
                return i
        return None

    def leaves_fancy(self):
        return [n for n in self.iternodes() if n.istip ]

    def lvsnms(self):
        return [n.label for n in self.iternodes() if n.istip ]

    def iternodes(self,order="preorder"):
        if order.lower() == "preorder":
            yield self
        for child in self.children:
            for d in child.iternodes(order):
                yield d
        if order.lower() == "postorder":
            yield self
    
    def prune(self):
        p = self.parent
        if p != None:
            p.remove_child(self)
        return p
    
    def get_newick_repr_paint(self):
        ret = ""
        painted_children = []
        for i in self.children:
            if "paint" in i.data:
                painted_children.append(i)
        for i in range(len(painted_children)):
            if i == 0:
                ret += "("
            ret += painted_children[i].get_newick_repr_paint()
            if i == len(painted_children)-1:
                ret += ")"
            else:
                ret += ","
        if self.label != None and "paint" in self.data:
            ret += self.label
        return ret

    def get_newick_repr(self,showbl=False):
        ret = ""
        for i in range(len(self.children)):
            if i == 0:
                ret += "("
            ret += self.children[i].get_newick_repr(showbl)
            if i == len(self.children)-1:
                ret += ")"
            else:
                ret += ","
        if self.label != None:
            ret += self.label
        if showbl == True:
            ret += ":" + str(self.length)
        return ret

    def get_newick_repr_note(self,showbl=False):
        ret = ""
        for i in range(len(self.children)):
            if i == 0:
                ret += "("
            ret += self.children[i].get_newick_repr_note(showbl)
            if i == len(self.children)-1:
                ret += ")"
            else:
                ret += ","
        if self.label != None:
            ret += self.label
        if len(self.note) > 0:
            ret += "["+self.note+"]"
        if showbl == True:
            ret += ":" + str(self.length)
        return ret

    def set_height(self):
        if len(self.children) == 0:
            self.height = 0
        else:
            tnode = self
            h = 0
            while len(tnode.children) > 0:
                if len(tnode.children) == 1:
                    tnode = tnode.children[0]
                else:
                    if tnode.children[1].length < tnode.children[0].length:
                        tnode = tnode.children[1]
                    else:
                        tnode = tnode.children[0]
                h += tnode.length
            self.height = h

    def set_dist_root(self):
        self.droot = 0
        if self.parent != None:
            cn = self
            while cn.parent != None:
                self.droot += 1
                cn = cn.parent

