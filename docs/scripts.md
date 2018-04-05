---
layout: page
title: Scripts
permalink: /scripts/
---

## Scripts
PyPHLAWD contains an array of scripts, many of which can be run independently. Below is a list of scripts and their functionality.

### Functions

-`setup_clade.py` This is the main program and will execute the clustering analysis. To run you will need to specify your clade of
interest, a database as downloaded by [phlawd_db_maker](https://github.com/blackrim/phlawd_db_maker), and a premade outdirectory
for the outputs of the analysis to be placed in. EX: `python setup_clade.py CLADE PHLAWD_DB.db OUTDIR/`
