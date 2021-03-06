#!/Users/colinjohn/anaconda2/envs/astro2/bin/python

import fakestars
import numpy as np
import imarith
import pyfits
from matplotlib import pyplot as plt
from astropy.io import fits
from astropy.utils.data import download_file
import sys
import random


image_file = "nimrud_IR_e02-e01_sub_masked.fits"
out_file = "testFileA.fits"
outfile2 = "testFileB.fits"
differenceFile = "testFileA_B.fits"
psf = "p330e_f160w_60mas_psf_model.fits"
hdu_list = fits.open(image_file)
data1 = hdu_list[0].data 
"""offset method creates a random offset decimal up to four decimal places"""
def offset():
   off = round(random.uniform(0.1, 1.0), 4)
   print off
   return off


off = offset()
mag = 25.12
"""conversion method, converts from (vega) magnitude to flux"""
def conversion(mag):
  from hstphot import hstphot as a
  zp = a.getzpt("testFileA.fits")
  print zp
  const = -.173718
  flux = (mag-zp)/const
  return flux
con =conversion(mag)
print con
test = np.array([[1664.283, 1714.017], [780.01, 1059.017], [1684.28, 1734.293],[123.123, 123.123],[456.12, 456.12],[345.12, 345.12],[653.1, 512.1],[1200.1, 2200.2]])
print test.dtype
print test.shape
test2 = np.array([[1664.283, 1714.017], [780.01, 1059.017], [1684.28, 1734.293], [1.00,1.00], [542.12, 345.12], [1231.1, 1243.12],[678.12, 987.65]])
diff = np.array([[703, 1460], [1684, 1800], [1266, 666]])
diff2 = np.array([[2280.283, 2280.283], [2280.283, 2280.283], [2280.283, 2280.283]])

fluxscale = np.array([con,2, 3,4,2,1, 2,1])

print " "
print test
print fluxscale
coordsys = 'xy'
verbose = True
name = sys.argv[1]
minimum = sys.argv[2]
maximum = sys.argv[3]
spacing = sys.argv[4]
"""Plant Grid method takes in a name of a difference file, a minimum value for brightness,
   a maximum value for brightness, and the spacing between"""
def plantGrid(name, minimum, maximum, spacing):
  """get the name and parameters from the command line"""
  name = sys.argv[1]
  minimum = sys.argv[2]
  maximum = sys.argv[3]
  minimum = int(minimum)
  maximum = int(maximum)
  #convert to flux
  min1 = conversion(minimum)
  max1 = conversion(maximum)
  min1 = int(min1)
  max1 = int(max1)
  #brightness = [random.uniform(min1, max1) for _ in xrange(len(position))]
  #print brightness
  spacing = sys.argv[4]
  spacing = float(spacing)
  print len(data1)
  #create the position array for x values
  x = np.arange(6, len(data1), spacing)
  #create the position array for y values
  y = np.arange(6, len(data1), spacing)
  x2 = np.arange(6, len(data1), spacing)
  y2 = np.flipud(y)
  
  #combine both arrays to form a grid
  position = np.column_stack((x,y))
  position2 = np.column_stack((x2,y2))
  
  #combine both lines of grid to one array
  position = np.concatenate((position, position2), axis = 0)
  
  #create a random brightness array between the min and max values
  brightness = np.array([random.uniform(min1, max1) for _ in range(0,len(position))])
  
  #add to image file and subtract
  fakestars.addtofits(name, out_file, psf, position, brightness, coordsys, verbose)
  fakestars.addtofits(name, outfile2, psf, position, brightness, coordsys, verbose)
  imarith.imsubtract(out_file, outfile2, differenceFile, clobber=True)
 

plantGrid(name, minimum, maximum, spacing)


imarith.imsubtract(out_file, outfile2, differenceFile, clobber=True)



"""

CODE FOR 2D GAUSSIAN PLANTING


hdu_list = fits.open(image_file)
hdu_list.info()
hdu_list1 = hdu_list[0].header
hdu_list1['comment'] = strPose
hdu_list1['comment'] = strPose2

hdu_list1['comment']
def makeGaussian(size, fwhm = 3, center=None):

    size is the length of a side of the square
    fwhm is full-width-half-maximum, which
    can be thought of as an effective radius.

    x = np.arange(0, size, 1, float)
    y = x[:,np.newaxis]

    if center is None:
        x0 = y0 = size // 2
    else:
        x0 = center[0]
        y0 = center[1]

    return np.exp(-4*np.log(2) * ((x-x0)**2 + (y-y0)**2) / fwhm**2)




image_data = hdu_list[0].data
print(type(image_data))
print(image_data.shape)


image_data[0:3,0:3] = makeGaussian(3,1, center = None)



#image_data = a_final
hdu_list.writeto('testFile.fits')

hdu_list.close()
"""
