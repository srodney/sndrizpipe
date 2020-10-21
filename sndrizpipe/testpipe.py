__author__ = 'srodney'



# TODO : add a test that uses the command-line interface
# command-line test :
# sndrizzle --filters F160W  --doall --mjdmin 56010 --mjdmax 56300 --ra 189.156538 --dec 62.309147  --refcat 'goodsn_mosaic.cat' colfax

print ('starting, and unzipping the tgz file')
import os

import sys
sys.path.insert(1, '.')

import sndrizpipe
import sndrizpipe.runpipe_cmdline
#from sndrizpipe.runpipe_cmdline import runpipe

#import urllib.request, urllib.error, urllib.parse
import os
import sys
import shutil
#import time



def colfaxtest():
    # TODO :  fix this so it fetches
    # fetch the test data from the MAST archive with astroquery
    colfaxfltlist = ['iboeabosq_flt.fits', 'ibtm7mldq_flt.fits',
                     'ibtmadmjq_flt.fits', 'ibwjcbd3q_flt.fits',
                     'iboeabowq_flt.fits', 'ibtm7mlgq_flt.fits',
                     'ibtmadmnq_flt.fits', 'ibwjcbdbq_flt.fits']

    # if not os.path.isdir('colfax.flt'):
    #    os.mkdir('colfax.flt')
    # shutil.remove

    tgzfile = os.path.realpath( './colfax_test.tgz' )
    print ('tgzfile', tgzfile)
    os.system( 'tar -xvzf %s'%tgzfile )

    #os.environ["iref"] = ""
    #os.environ["jref"] = ""

    sndrizpipe.runpipe_cmdline.runpipe('colfax', doall=True, tempepoch=1)
