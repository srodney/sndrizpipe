#!/Users/colinjohn/anaconda2/envs/astro2/bin/python

from astropy.stats import sigma_clipped_stats
from photutils import DAOStarFinder
from astropy.io import fits
from astropy.table import Table
import sys


image_file = sys.argv[1]
hdu_list = fits.open(image_file)
data = hdu_list[0].data 

data1 = data[0:len(image_file), 0:len(image_file)]
mean, median, std = sigma_clipped_stats(data, sigma = 3.0, iters =5)
print(mean, median, std)
find = DAOStarFinder(fwhm = 3.0, threshold = 5.*std)
sn = find(data-median)

outputFile = image_file + ".detectionTable"
f = open(outputFile, 'w')
f.write(str(sn))

for i in sn:
    f.write(str(i))


import matplotlib.pyplot as plt
from astropy.visualization import SqrtStretch
from astropy.visualization.mpl_normalize import ImageNormalize
from photutils import CircularAperture



positions = (sn['xcentroid'], sn['ycentroid'])

apertures = CircularAperture(positions, r=6.)
norm = ImageNormalize(stretch=SqrtStretch())
plt.imshow(data, cmap='Greys', origin='lower', norm=norm)
apertures.plot(color='blue', lw=1.5, alpha=0.5)
f.close()
plt.savefig('sourcesDetected.png')