import sys
import os
import seq
import HTML as hl

htmlbegin ="""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.1/css/bootstrap.min.css" integrity="sha384-WskhaSGFgHYWDcbwN70/dfYBj47jz9qbsMId/iRN3ewGhXQFZCSftd1LZCfmhktB" crossorigin="anonymous">
    <title>PyPHLAWD results</title>
</head>
<body>
<main role="main" class="container">
"""

htmlend ="""
<script src="https://code.jquery.com/jquery-3.3.1.slim.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.3/umd/popper.min.js" integrity="sha384-ZMP7rVo3mIykV+2+9J3UJ46jBk0WLaUAdn689aCwoqbBJiSnjAK/l8WvCWPIPm49" crossorigin="anonymous"></script>
<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.1.1/js/bootstrap.min.js" integrity="sha384-smHYKdLADwkXOn1EmN1qk/HfnUcbVRZyYmZ4qpPea6sjB/pTJ0euyQp0Mk8ck+5T" crossorigin="anonymous"></script>
</main>


</body>
</html>
"""

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
        try:
            avl = avl/float(num)
        except:
            avl = 0.0
        cli[i] = sps
        if len(sps) > 2:
            clns.append([hl.link(i,"clusters/"+i),len(sps),format(avl,'.4f'),firstdef])
    
    clns = sorted(clns, key=lambda x: x[1], reverse=True)
    #clns.insert(0,["<b>name</b>","<b>num_species</b>","<b>avg unaln len</b>","<b>defline</b>"])
    
    htmlf = open(outfile,"w")
    fhr = None
    if os.path.isfile(cld+"/../../info.html"):
        fhr = [hl.link('back','../info.html')]
    else:
        fhr = [""]   
    links = []
    for i in os.listdir(cld+"/../"):
        if os.path.isdir(cld+"/../"+i) and "clusters" not in i:
            #htmlc = hl.link("  "+i+"  ",i+"/info.html")
            links.append([hl.link("  "+i+"  ",i+"/info.html")])
            #htmlf.write(htmlc)
    
    name = cld.split("/")[-2]
    htmlf.write(htmlbegin)
    htmlf.write('<div class="row"><div class="col">\n<pre>\n     ___       ___  __ ____   ___ _      _____ \n    / _ \__ __/ _ \/ // / /  / _ | | /| / / _ \ \n   / ___/ // / ___/ _  / /__/ __ | |/ |/ / // /\n  /_/   \_, /_/  /_//_/____/_/ |_|__/|__/____/ \n       /___/                results     </pre></div>\n')
    htmlf.write('<div class="col"><br><h1>'+name+'</h1></div>\n</div>\n')
    htmlf.write("<div class=\"row\">\n<div class=\"col-sm-3\">\n")
    htmlc = hl.table(links,style=None,border=None,cellpadding=None,classs="table",header_row=fhr)
    htmlf.write(htmlc)
    htmlf.write("</div>\n<div class=\"col\">\n")
    htmlc = hl.table(clns,style=None,border=None,cellpadding=None,classs="table",header_row=['name','num_species','avg len','defline'])
    htmlf.write(htmlc)
    htmlf.write("</div>\n</div>\n")
    htmlf.write(htmlend)
    htmlf.close()

#table file should be in the maindir 

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("python "+sys.argv[0]+" maindir")
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

