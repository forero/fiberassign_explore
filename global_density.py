import desimodel.footprint
from astropy.table import Table
import matplotlib.pyplot as plt
import numpy as np

def write_dens(filetype='std'):
    files = {"targets": "/global/cscratch1/sd/forero/testfiber/dark_large/mtl_large.fits", 
         "sky": "/global/cscratch1/sd/forero/fiberassign_explore/dark_large/sky_large.fits", 
         "std" : "/global/cscratch1/sd/forero/testfiber/dark_large/std_large.fits"
    }
    outfile = '{}_ndensity.txt'.format(filetype)
    print(files[filetype], outfile)
    f  = open(outfile, 'w')
    f.write("# TILEID RA DEC N\n")
    f.close()
    
    # Read the data
    datafile = files[filetype]
    data = Table.read(datafile)
    
    # Read the tiles with the fiberassignment counts
    counts = Table.read('tile_counts.txt', format='ascii')
    intiles = Table.read("/global/cscratch1/sd/forero/testfiber/dark_large/input_tiles.fits")
    jj = np.in1d(intiles['TILEID'], counts['TILEID'])
    tiles = intiles[jj]
    len(tiles)
    
    # trim the data
    ii =  desimodel.footprint.is_point_in_desi(tiles, data['RA'], data['DEC'])
    data = data[ii]
    
    # write the data
    n_tiles = len(tiles)
    for i in range(n_tiles):
        f = open(outfile, 'a')
        f.write('{}\t{:.2f}\t{:.2f}\t'.format(tiles[i]['TILEID'], tiles[i]['RA'], tiles[i]['DEC']))
        ii =  desimodel.footprint.is_point_in_desi(Table(tiles[i]), data['RA'], data['DEC'])
        f.write('{}\n'.format(np.count_nonzero(ii)))
        print(np.count_nonzero(ii), i, n_tiles)
        f.close()
