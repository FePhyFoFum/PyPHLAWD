# pyphlawd
Python version of PHLAWD

## Setup
PyPHLAWD should be easy to setup. 

### Requirements
You will need to have 
- a database created by `PHLAWD` or the `phlawd_db_maker` (_COMING SOON:_ or your own sequences)
- python
	- the libraries you need for python are sqlite3 and clint (for text coloring)
- mafft
- FastTree (if you have `treemake` on)
- blast

### Database
I would recommend that you use `phlawd_db_maker` to make the necessary sequence database. 

## Running 
There are two basic ways to run PyPHLAWD:
- `python setup_clade.py Dipsacales PHLAWD_DBS/pln.db OUTDIR/`
- `python setup_clade_bait.py Dipsacales bait_dir/ PHLAWD_DBS/pln.db OUTDIR/`

### Clustering runs

### Bait runs
In addition to the clustering runs (that will look at all the available data, you can also look at only the gene regions you're interest in (as the old PHLAWD).

#### Bait files
Bait files need to be in a directory and need to have the file ending `.fa` and need to be fasta files. This requirement is necessary in order to recognize which files are intended to be the bait in the directory (so you can have other files in the directory).

### Subsetting taxa
With either of the above runs types, you can limit what taxa are considered. For this, you will need a file that has an ncbi id on each line. These will be the only ones considered. Then you run like:
- `python setup_clade.py Dipsacales PHLAWD_DBS/pln.db OUTDIR/ taxalist` 
- `python setup_clade_bait.py Dipsacales bait_dir/ PHLAWD_DBS/pln.db OUTDIR/ taxalist` 

There is a helper script that will help make your taxa list file. If you have a file that has `Genus species` on each line, you can use the script 
- `python get_ncbi_ids_for_names.py names_file PHLAWD_DBS/pln.db > taxalist`

### conf.py
There is a configuration file that has some basic configuration settings. 

## Output
PyPHLAWD will make a bunch of directories. In each directory, there will be a `clusters` folder that has either the constructed bait files or the clusters. There is also an `info.html` file in each directory. If you open the root one (the one inside the main directory made) you will see the stats for each cluster/bait that has more than 3 taxa. There will be an alignment file (with `.aln` file ending for each file) and a `.tre` if you have treemake on.

## Runtime considerations 
