__author__ = 'srodney'



# TODO : add a test that uses the command-line interface
# command-line test :
# sndrizzle --filters F160W  --doall --mjdmin 56010 --mjdmax 56300 --ra 189.156538 --dec 62.309147  --refcat 'goodsn_mosaic.cat' colfax

import os
import glob
import sys
#sys.path.insert(1, '.')

import sndrizpipe
import sndrizpipe.runpipe_cmdline
#from sndrizpipe.runpipe_cmdline import runpipe

import os
from astroquery.mast import Observations
#import urllib.request, urllib.error, urllib.parse
import shutil
#import time



def doalltest(refetch=False, testcase='stone'):
    """A full soup-to-nuts test run, using HST CANDELS SN data"""

    if testcase=='colfax':
        fltlist = ['iboeabosq_flt.fits', 'ibtm7mldq_flt.fits',
                   'ibtmadmjq_flt.fits', 'ibwjcbd3q_flt.fits',
                   'iboeabowq_flt.fits', 'ibtm7mlgq_flt.fits',
                   'ibtmadmnq_flt.fits', 'ibwjcbdbq_flt.fits']
        # TODO : make an obsidlist for colfax
    else:  # STONE
        fltlist = ['ib3722j3q_flt.fits', 'ib3722jgq_flt.fits',
                   'ib3722jiq_flt.fits', 'ib3722jvq_flt.fits',
                   'ic6hsbe0q_flt.fits', 'ic6hsbebq_flt.fits']
        obsidlist = ['2003839770', '2002967374', '2002967377']

    if not os.path.isdir(testcase+'.flt'):
        os.mkdir(testcase+'.flt')

    # Clean out old flt files in the .flt dir
    oldfltlist = glob.glob(testcase+'.flt/*flt.fits')
    for oldfltfile in oldfltlist:
        os.remove(oldfltfile)

    # Fetch files from the MAST archive
    for obsid in obsidlist:
        ## TODO:  The download_file function is coming in a future astroquery release
        #product = 'mast:HST/product/'+fltfile
        #result = mastObs.download_file(
        #    product, local_path=fltfilepath)
        Observations.download_products(
            obsid,
            productSubGroupDescription=["FLT"],
            extension="fits",
            download_dir=testcase+'.flt')
    fltdownloadedlist = glob.glob(os.path.join(testcase+'.flt','mastDownload',
                                               'HST','*','*flt.fits'))

    # Clean up the download cruft
    for fltfile in fltdownloadedlist:
        shutil.move(fltfile, testcase+".flt")
    shutil.rmtree(os.path.join(testcase+'.flt','mastDownload'))

    sndrizpipe.runpipe_cmdline.runpipe('stone', ra=189.319875, dec=62.278167,
                                       doall=True, tempepoch=1)
