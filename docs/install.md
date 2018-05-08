---
layout: page
title: Install
permalink: /install/
---

## Setup

PyPHLAWD should be easy to setup (or that is the hope). There are a few programs that it requires (listed below). These need to be in the PATH (so when you type the program, like `mafft`, it just runs). You should use the instructions on these pages to help you install for your machine. If you are running linux, it is significantly simpler because many of these are in your repos (e.g., `sudo apt-get`...).

### Requirements

- a database created by [`phlawd_db_maker`](https://github.com/blackrim/phlawd_db_maker) (_COMING SOON:_ or your own sequences).
- python : version 2
  - you will also need python libraries for [sqlite3](https://docs.python.org/3/library/sqlite3.html#module-sqlite3), [networkx](https://github.com/networkx/networkx), and [clint](https://pypi.python.org/pypi/clint) (for text coloring)
  - These libraries can be installed using pip `sudo pip install networkx` and `sudo pip install clint`. If you are running linux you can probably do `sudo apt install python-networkx python-sqlite python-clint`
- [mafft](http://mafft.cbrc.jp/alignment/software/) : You will need a recent version (>=v7.3 works well) that has threading and merging. If you are running linux, you can probably run `sudo apt install mafft`
- [FastTree](http://www.microbesonline.org/fasttree/) : (if you have `treemake` on)
- [blast+](https://blast.ncbi.nlm.nih.gov/Blast.cgi?PAGE_TYPE=BlastDocs&DOC_TYPE=Download) : Currently, this runs `blastn` and `makeblastdb` from the blast+ package. Soon, it will use `blastp` as well.
- [mcl](http://micans.org/mcl/) : Markov clustering for the clustering runs (you won't need this if you only bait). You can install this with `sudo apt install ncbi-blast+`
- [phyx](https://github.com/FePhyFoFum/phyx/)
  - Relies upon `pxssort`, `pxrevcomp`, `pxrmt`, `pxcat`, and `pxrms`. You can only install these if you like by specifying `make pxssort pxrevcomp pxrmt pxcat pxrms` instead of just `make` or `make all` when installing `phyx`. More instructions can be found at the [`phyx` website](https://github.com/FePhyFoFum/phyx/).
- [cython](cython.org/) : This is optional but will speed up some functions
  -cython can be installed using pip `sudo pip install cython` or if you are running linux, you can do `sudo apt install python-cython`

### Database

We would recommend that you use `phlawd_db_maker` to make the necessary sequence database. You will want to make a database (e.g., `phlawd_db_maker pln ~/PHLAWD_DBS/pln.db`). This will be used if you are using NCBI sequences (if you are using something else, see that section below). 

### Setup

Now that you have a database and you have the dependencies installed, you can compile the `cython` part. This will make operations on larger trees much faster. 

## Using virtualenv for clusters or other systems
There are some situations where it might be easier to install PyPHLAWD using virtualenv. In particular, this may be the easiest way to install on a cluster. To do this, you will need to install `pip` (or already have `pip` installed). If you have a linux distribution with a package manager, you can install it with that. If you have to get and install pip, you can use the instructions [here](http://thelazylog.com/install-python-as-local-user-on-linux/). Basically,  `wget --no-check-certificate https://bootstrap.pypa.io/get-pip.py -O - | python - --user`, then edit `~/.bashrc` or `~/.bashrc_profile` with `export PATH=$HOME/.local/bin:$PATH`. When you do `which pip` after this, it should point to `~/.local/bin`. 

After `pip` is installed, you can then follow the instructions [here](http://docs.python-guide.org/en/latest/dev/virtualenvs/). Basically, `pip install virtualenv`, `mkdir PyPHLAWD_env`, `virtualenv PyPHLAWD_env`, `source PyPHLAWD_env/bin/activate`, and `cd PyPHLAWD_env`. Then you can use pip to install the other python bits (cython, networkx, clint, and sqlite3). Thanks to Javier Igea for working some of this out.