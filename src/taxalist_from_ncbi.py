import sys

from Bio import Entrez


def main():
    '''
    Returns a file of NCBI IDs for a given taxanomic group suitable for subsetting.

    CMD line args:

        search_terms = NCBI search terms (check spelling)
        output_file  = where the IDs are written
        retmax       = max number of records returned from NCBI
        
    '''

    Entrez.email = 'fundscience@wh.gov'
    db_type = 'nucleotide'
    search_terms = sys.argv[1]
    output_file = sys.argv[2]
    retmax = sys.argv[3]
    returned_ids = esearch(search_terms, db_type)
    make_taxalist(returned_ids, output_file)

    return

def esearch(search_terms, db_type):
    
    handle = Entrez.esearch(db=db_type, term = search_terms, idtype="acc", retmax = 10000)
    record = Entrez.read(handle)
    print('Search returned %s results.\n' %record["Count"])
    
    ids = record["IdList"]

    return ids

def make_taxalist(ids, output):
    
    with open(output, 'a') as fh:

        for i in ids:
            fh.write(f'{i}\n')

    return

if __name__ == '__main__':

    main()