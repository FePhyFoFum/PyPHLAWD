#cython cnode.pyx
#gcc -shared -pthread -fPIC -fwrapv -O2 -Wall -fno-strict-aliasing -I/usr/include/python2.7 -o cnode.so cnode.c
python cython_setup.py build_ext --inplace
