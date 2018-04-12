---
layout: page
title: Install
permalink: /install/
---

## Setup
PyPHLAWD should be easy to setup (or that is the hope). There are a few programs that it requires (listed below). These need to be in the PATH (so when you type the program, like `mafft`, it just runs). You should use the instructions on these pages to help you install for your machine. If you are running linux, it is significantly simpler because many of these are in your repos (e.g., `sudo apt-get`...). 

### Requirements
- a database created by `PHLAWD` or the `phlawd_db_maker` (_COMING SOON:_ or your own sequences). I recommend [phlawd_db_maker](https://github.com/blackrim/phlawd_db_maker) as it is simpler.
- python : version 2 
	- you will also need python libraries for [sqlite3](https://docs.python.org/3/library/sqlite3.html#module-sqlite3), [networkx](https://github.com/networkx/networkx), and [clint](https://pypi.python.org/pypi/clint) (for text coloring)
	- These libraries can be installed using pip `sudo pip install networkx` and `sudo pip install clint`
- [mafft](http://mafft.cbrc.jp/alignment/software/) : You will need a recent version (>=v7.3 works well) that has threading and merging. 
- [FastTree](http://www.microbesonline.org/fasttree/) : (if you have `treemake` on)
- [blast+](https://blast.ncbi.nlm.nih.gov/Blast.cgi?PAGE_TYPE=BlastDocs&DOC_TYPE=Download) : Currently, this runs `blastn` and `makeblastdb` from the blast+ package. Soon, it will use `blastp` as well.
- [mcl](http://micans.org/mcl/) : Markov clustering for the clustering runs (you won't need this if you only bait)
- [phyx](https://github.com/FePhyFoFum/phyx/) : Relies upon pxssort, pxrevcomp, pxrmt, pxcat, and pxrms
- [cython](cython.org/) : This is optional but will speed up some functions
	-cython can be installed using pip `sudo pip install cython`

### Database
I would recommend that you use `phlawd_db_maker` to make the necessary sequence database. You will want to make a database (e.g., `phlawd_db_maker pln ~/PHLAWD_DBS/pln.db`). This will be used if you are using NCBI sequences (if you are using something else, see that section below). 
