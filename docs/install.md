---
layout: page
title: Install
permalink: /install/
---

## Setup

PyPHLAWD should be easy to setup (or that is the hope). There are a few programs that it requires (listed below). These need to be in the PATH (so when you type the program, like `mafft`, it just runs). You should use the instructions on these pages to help you install for your machine. If you are running linux, it is significantly simpler because many of these are in your repos (e.g., `sudo apt-get ...`). If you are running mac, you can probably install many of not all of these using brew (e.g., `brew install ...`).

### Requirements

- a database created by [`phlawd_db_maker`](https://github.com/blackrim/phlawd_db_maker) (_COMING SOON:_ or your own sequences). You can grab a premake one for many databases [here](http://141.211.236.35:10998/).
- python : version 2
  - you will also need python libraries for [sqlite3](https://docs.python.org/3/library/sqlite3.html#module-sqlite3), [networkx](https://github.com/networkx/networkx), and [clint](https://pypi.python.org/pypi/clint) (for text coloring)
  - These libraries can be installed using pip `sudo pip install networkx` and `sudo pip install clint`. If you are running linux you can probably do `sudo apt install python-networkx python-sqlite python-clint`
- [mafft](http://mafft.cbrc.jp/alignment/software/) : You will need a recent version (>=v7.3 works well) that has threading and merging. If you are running linux, you can probably run `sudo apt install mafft` or `brew install mafft` on Mac (with homebrew)
- [FastTree](http://www.microbesonline.org/fasttree/) : (if you have `treemake` on)
- [blast+](https://blast.ncbi.nlm.nih.gov/Blast.cgi?PAGE_TYPE=BlastDocs&DOC_TYPE=Download) : Currently, this runs `blastn` and `makeblastdb` from the blast+ package. Soon, it will use `blastp` as well. You can install this with `sudo apt install ncbi-blast+` or `brew install blast` on Mac (with homebrew)
- [mcl](http://micans.org/mcl/) : Markov clustering for the clustering runs (you won't need this if you only bait). If you are on linux, you can run `sudo apt install mcl` or `brew install brewsci/bio/mcl` on Mac (with homebrew)
- [phyx](https://github.com/FePhyFoFum/phyx/)
  - Relies upon `pxssort`, `pxrevcomp`, `pxrmt`, `pxcat`, and `pxrms`. You can only install these if you like by specifying `make pxssort pxrevcomp pxrmt pxcat pxrms` instead of just `make` or `make all` when installing `phyx`. Then you want to do `sudo make install` so these go in your PATH. More instructions can be found at the [`phyx` website](https://github.com/FePhyFoFum/phyx/).
- [cython](cython.org/) : This is optional but will speed up some functions
  -cython can be installed using pip `sudo pip install cython` or if you are running linux, you can do `sudo apt install cython`

### Database

There are _some_ prebuilt databases [here](http://141.211.236.35:10998/). The files are big (many GBs so it may take time). If there is one that isn't listed, put an [issue](https://github.com/FePhyFoFum/PyPHLAWD/issues) in github or make one with the instructions below.

We would recommend that you use `phlawd_db_maker` to make the necessary sequence database. You will want to make a database (e.g., `phlawd_db_maker pln ~/PHLAWD_DBS/pln.db`). This will be used if you are using NCBI sequences (if you are using something else, see that section below). 

### Post installation setup

Now that you have a database and you have the dependencies installed, you should clone the repository with this command `git clone https://github.com/FePhyFoFum/PyPHLAWD.git`. Then we should compile the `cython` part. This will make operations on larger trees much faster. To compile this, go into the `src` directory (`cd PyPHLAWD/src`) and type `bash compile_cython.sh`. Hopefully `cython` was installed and there was just some output but no error. You don't need to do anything else. Stuff will just work faster. The only other thing you will need to do (and this is discussed more in the [runs](https://fephyfofum.github.io/PyPHLAWD/runs/) page) and that is change the `conf.py` file line that starts with `DI=...` (should be the second line). Make sure that that points to your PyPHLAWD `src` directory. You should be ready for the [runs](https://fephyfofum.github.io/PyPHLAWD/runs/) page.

### Updating PyPHLAWD

Occasionally, there will be updates to PyPHLAWD and you will want to pull to the most recent version. You can do that by simply running `git pull` inside your PyPHLAWD directory. *However*, if you have changed files (you probably have changed `conf.py`), you will want to save those somewhere first (I would just copy the file somewhere temporarily). Then you can run `git checkout conf.py` (or whatever other files you have changed) to revert them. _Then_ do `git pull` and move your edited files back. You may want to check the `git pull` output to make sure the files you have changed were not changed in the source code. If so, you probably want to merge them. If there are more questions about this, post an issue and we will add a gif or more instructions.

## Using virtualenv for clusters or other systems

There are some situations where it might be easier to install PyPHLAWD using virtualenv. In particular, this may be the easiest way to install on a cluster. To do this, you will need to install `pip` (or already have `pip` installed). If you have a linux distribution with a package manager, you can install it with that. If you have to get and install pip, you can use the instructions [here](http://thelazylog.com/install-python-as-local-user-on-linux/). Basically,  `wget --no-check-certificate https://bootstrap.pypa.io/get-pip.py -O - | python - --user`, then edit `~/.bashrc` or `~/.bashrc_profile` with `export PATH=$HOME/.local/bin:$PATH`. When you do `which pip` after this, it should point to `~/.local/bin`.

After `pip` is installed, you can then follow the instructions [here](http://docs.python-guide.org/en/latest/dev/virtualenvs/). Basically, `pip install virtualenv`, `mkdir PyPHLAWD_env`, `virtualenv PyPHLAWD_env`, `source PyPHLAWD_env/bin/activate`, and `cd PyPHLAWD_env`. Then you can use pip to install the other python bits (cython, networkx, clint, and sqlite3). Thanks to Javier Igea for working some of this out.
