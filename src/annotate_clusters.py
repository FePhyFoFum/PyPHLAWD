import sys
import os
import seq
import HTML as hl

def make_cluster_table(cld, idn,idd, outfile):
    cli = {}
    clns = []
    for i in os.listdir(cld):
        if ".fa" not in i:
            continue
        sps = set()
        firstdef = None
        num = 0
        avl = 0
        for j in seq.read_fasta_file_iter(cld+"/"+i):
            sps.add(idn[j.name])
            firstdef = idd[j.name]
            avl += len(j.seq)
            num += 1
        avl = avl/float(num)
        cli[i] = sps
        if len(sps) > 2:
            clns.append([hl.link(i,"clusters/"+i),len(sps),avl,firstdef])
    
    clns = sorted(clns, key=lambda x: x[1], reverse=True)
    clns.insert(0,["<b>name</b>","<b>num_species</b>","<b>avg unaln len</b>","<b>defline</b>"])
    
    htmlf = open(outfile,"w")
    links = []
    if os.path.isfile(cld+"/../../info.html"):
        #htmlc = hl.link('back','../info.html')
        links.append([hl.link('back','../info.html')])
        #htmlf.write(htmlc)
    
    for i in os.listdir(cld+"/../"):
        if os.path.isdir(cld+"/../"+i) and "clusters" not in i:
            #htmlc = hl.link("  "+i+"  ",i+"/info.html")
            links.append([hl.link("  "+i+"  ",i+"/info.html")])
            #htmlf.write(htmlc)
    
    name = cld.split("/")[-2]
    htmlf.write("<h1>"+name+"</h1>")
    htmlf.write("<div style=\"float: left\">\n")
    htmlc = hl.table(links,style="border: 2px solid #000000; border-collapse: collapse;")
    htmlf.write(htmlc)
    htmlf.write("</div>\n<div style=\"float: left\">\n")
    htmlc = hl.table(clns,width=600,style="border: 2px solid #000000; border-collapse: collapse;")
    htmlf.write(htmlc)
    htmlf.write("</div>\n")
    htmlf.close()

#table file should be in the maindir 

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "python "+sys.argv[0]+" maindir"
        sys.exit(0)
    cld = sys.argv[1]
    #take off the trailing slash if there is one
    if cld[-1] == "/":
        cld = cld[0:-1]
    idn = {}
    idd = {}
    tf = open(cld+"/"+cld.split("/")[-1]+".table","r")
    for i in tf:
        spls = i.strip().split("\t")
        idn[spls[3]] = spls[4]
        idd[spls[3]] = spls[5]
    tf.close()
    for root, dirs, files in os.walk(cld,topdown=True):
        if "clusters" in root:
            continue
        if "clusters" in dirs:
            make_cluster_table(root+"/clusters", idn,idd, root+"/info.html")

