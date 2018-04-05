---
layout: page
title: Scripts
permalink: /scripts/
---

## Scripts
PyPHLAWD contains an array of scripts, many of which can be run independently. Below is a list of scripts and their functionality.

### Main Programs

-`setup_clade.py` This is the main program and will execute the clustering analysis. To run you will need to specify your clade of
interest, a database as downloaded by [phlawd_db_maker](https://github.com/blackrim/phlawd_db_maker), and a premade outdirectory
for the outputs of the analysis to be placed in. 
EX: `python setup_clade.py CLADE PHLAWD_DB.db OUTDIR/`

-`setup_bait_clade.py` This runs the same analysis as `setup_clade.py`, however, it allows you to provide your own bait sequences.
These sequences should be in fasta format and put in a directory. If the sequences you have are not in fasta format, the program
`pxs2fa` from the suite [phyx](https://github.com/FePhyFoFum/phyx) can be used to convert it.
EX: `python setup_clade.py CLADE BAIT_DIR/ PHLAWD_DB.db OUTDIR/`

### Other Scripts

-`add_clade_cluster.py` This will run during the main program or can be run separately to combine clusters together. The user specifies
a folder with clusters to combine. This should contain a set of fasta files that end in `.fa` and their corresponding alignments ending
in `.aln`. The user can also specify a log file or alternatively the logfile `pyphlawd.log` will have the information written to.
EX: `python add_clade_cluster.py CLUSTER_FOLDER OUT_FOLDER OPTIONAL_LOGFILE`
