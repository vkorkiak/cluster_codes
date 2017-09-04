#! /bin/python

import os
import sys

def install_rigaut_contrib(name):
    if not os.path.exists(name):
        os.system('git clone https://github.com/frigaut/'+name)
        if name == 'yao':
            os.system('cd '+name+'; cp Makefile.template Makefile')
        os.system('cd '+name+'; yorick -batch make.i')
        os.system('cd '+name+'; make')
        os.system('cd '+name+'; make install')
    else:
        os.system('cd '+name+'; git pull')
        os.system('cd '+name+'; yorick -batch make.i')
        os.system('cd '+name+'; make clean')
        os.system('cd '+name+'; make')
        os.system('cd '+name+'; make install')


contribs = ['yorick-yutils', 'yorick-imutil', 'yorick-hdf5', 'yorick-soy', 'yao']

if len(sys.argv) > 1:
    # print('Argument: %s' % str(sys.argv[1]))
    if sys.argv[1] == 'clean':
        print('Deleting contribs..')
        for contrib in contribs:
            os.system('rm -rf '+contrib)
        print('DONE')
        quit()

print('Installing contribs...')    

for contrib in contribs:
    install_rigaut_contrib(contrib)

print('DONE')
