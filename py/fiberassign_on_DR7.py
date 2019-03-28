# Reuses some info from Stephen Bailey shared on [desi-data 3401] "running fiber assignment on a real target catalog"
# 
# This code uses DR7 data to run fiberassign on it.
#
import os
import subprocess
from astropy.table import Table, join, vstack
import numpy as np
from desitarget.targetmask import desi_mask, bgs_mask, mws_mask, obsmask, obsconditions
import fitsio
import glob
from desisim.quickcat import quickcat
import desimodel.io
import argparse
import desitarget.mtl

parser = argparse.ArgumentParser(description='Define parameters')
parser.add_argument('--program', type=str, required=True,
                    help='dark or bright')
args = parser.parse_args()

program = args.program

#directories
datadir = "./".format(program)
fiberdir = "./{}_fiber_output/".format(program)
if not os.path.exists(datadir):
    os.makedirs(datadir)  
if not os.path.exists(fiberdir):
    os.makedirs(fiberdir)  

#filenames
paths = {"targets": "/project/projectdirs/desi/target/catalogs/dr7.1/0.27.0/", 
         "skies": "/project/projectdirs/desi/target/catalogs/dr7.1/0.27.0/", 
         "gfas": "/project/projectdirs/desi/target/catalogs/dr7.1/0.27.0/",
}

names = {"targets": "dr7.1-0.27.0.fits", "skies":"dr7.1-0.27.0.fits", "gfas": "dr7.1-0.27.0.fits"}

mtlfile = os.path.join(datadir, 'mtl_{}'.format(names["targets"]))
starfile = os.path.join(datadir, 'std_{}.fits'.format(program))
goodskyfile = os.path.join(datadir, 'sky_{}.fits'.format(program))
tilefile = os.path.join(datadir, "input_tiles_{}.fits".format(program))
targetfile = os.path.join(paths["targets"], "targets-{}".format(names["targets"]))
skyfile = os.path.join(paths["skies"], "skies-{}".format(names["skies"]))
gfafile = os.path.join(paths["gfas"], "gfas-{}".format(names["gfas"]))


# tile selection

if not os.path.exists(tilefile):
    tiles = desimodel.io.load_tiles()
    bright = tiles['PROGRAM']=='BRIGHT'
    
    if program=="bright":
        Table(tiles[bright]).write(tilefile)
    else:
        Table(tiles[~bright]).write(tilefile)

    print("wrote tiles to {}".format(tilefile))

#compute MTL
if not os.path.exists(mtlfile):
    print('computing mtl for targets')
    import desitarget.mtl
    targetdata = fitsio.read(targetfile, 'TARGETS')
    tmp_mtl = desitarget.mtl.make_mtl(targetdata)
    tmp_mtl.meta['EXTNAME'] = 'MTL'
    tmp_mtl.write(mtlfile)

    #print some stats
    print('MWS_TARGETS: {}'.format(np.count_nonzero(tmp_mtl['MWS_TARGET']!=0)))
    print('BGS_TARGETS: {}'.format(np.count_nonzero(tmp_mtl['BGS_TARGET']!=0)))
    print('DESI_TARGETS: {}'.format(np.count_nonzero(tmp_mtl['DESI_TARGET']!=0)))
    print('finished computing mtl')
    
# Running fiberassign
cmd = "fba_run --targets {} ".format(mtlfile)
cmd += " {} ".format(skyfile)
cmd += " --footprint {} ".format(tilefile)
cmd += " --dir {} ".format(fiberdir)
print(cmd)
print('starting fiberassign')
os.system(cmd)
print('finished fiberassign')


# merge result
cmd = "fba_merge_results --targets {} ".format(mtlfile)
cmd += " {} ".format(skyfile)   
cmd += " --out {}".format(fiberdir)
cmd += " --dir {}".format(fiberdir)
print(cmd)
print('starting merge')
os.system(cmd)
print('finished merge')
