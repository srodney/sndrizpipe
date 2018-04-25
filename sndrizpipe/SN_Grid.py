#!/Users/colinjohn/anaconda2/envs/astro2/bin/python

import numpy as np
import fakestars
import imarith
import pyfits
from astropy.io import fits
import random
import sys
from hstphot import hstphot as a
import math


name = sys.argv[1]
minimum = sys.argv[2]
maximum = sys.argv[3]
spacing = sys.argv[4]
spacing = float(spacing)
minimum = int(minimum)
maximum = int(maximum)
#print arr.shape
out_file =  name + "fakes_plantedA.fits"
outfile2 = name + "fakes_plantedB.fits"
differenceFile = name+ "fakes_planted_diff.fits"
psf = "p330e_f160w_60mas_psf_model.fits"

mag =25
zp = a.getzpt("testFileA.fits")
def conversion(mag):
  
  flux = 10**(-.4*(mag-zp))
  return flux


con =conversion(mag)
hdu_list = fits.open(name)
data1 = hdu_list[0].data 
print len(data1)
coordsys = 'xy'
verbose = True

iterVal = (len(data1)/spacing)
iterVal = iterVal-1
iterValTotal = iterVal*(iterVal)
arr = (iterValTotal,2)
arr = np.zeros(arr)
count = 0

#convert to flux
"""Testing grid stuff"""
min1 = conversion(minimum)
max1 = conversion(maximum)
min1 = int(min1)
max1 = int(max1)
mag=minimum
brightness = []
for i in np.arange(50, len(data1), 50):
    for j in np.arange(50,len(data1),50):
        
        #print i, j
        arr[count]= [i,j]
        if mag <=maximum:
          brightness.append(mag)
        else:
          mag=minimum
          brightness.append(mag)
        mag+=.05
        count +=1
        #print arr
conversion = np.vectorize(conversion)

brightness = conversion(brightness)

fakestars.addtofits(name, out_file, psf, arr, brightness, coordsys, verbose)
fakestars.addtofits(name, outfile2, psf, arr, brightness, coordsys, verbose)
imarith.imsubtract(out_file, outfile2, differenceFile, clobber=True)

