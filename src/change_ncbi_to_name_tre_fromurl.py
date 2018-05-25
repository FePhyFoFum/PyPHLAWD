import requests
import json
import sys
import tree_reader

def rename_tree(inurl,ts):
    url = inurl+'/rename_tree_ncbi'
    idss = "{\"newick\":\""+ts+"\"}"
    payload = json.loads(idss)
    headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
    r = requests.post(url, data=json.dumps(payload), headers=headers)
    
    ne = None
    unmatched = None
    if 'newick' in r.json():
        ne = r.json()['newick']
        unmatched = r.json()['unmatched_ott_ids']
    
    return ne,unmatched

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "python "+sys.argv[0]+" url filename"
        sys.exit(0)
    
    url = sys.argv[1]
    nw = tree_reader.read_tree_file_iter(sys.argv[2]).next()
    ne = nw.get_newick_repr(True)+";"
    ne,unmatached = rename_tree(url,ne)
    print ne