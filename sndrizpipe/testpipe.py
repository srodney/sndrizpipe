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
import urllib.request, urllib.error, urllib.parse
import os
import sys
import time
#from sndrizpipe.runpipe_cmdline import runpipe



#colfaxtest()
tgzfile = os.path.realpath( './colfax_test.tgz' )
print ('tgzfile', tgzfile)
os.system( 'tar -xvzf %s'%tgzfile )

os.environ["iref"] = ""
os.environ["jref"] = ""

sndrizpipe.runpipe_cmdline.runpipe('colfax', doall=True, tempepoch=1)






