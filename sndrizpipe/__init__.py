"""
2014.02.26  S.Rodney

A module for sorting HST imaging data into groups based on observation date 
and filter, then combining each epoch using astrodrizzle.

"""
__all__=[ "exposures","drizzle","badpix","register","imarith",
         "testpipe", "mkrefcat", "pseudodiff", "imcrop", "util"]
from . import exposures
from . import drizzle
from . import badpix
from . import register
from . import imarith
#from . import testpipe
from . import mkrefcat
from . import pseudodiff
from . import imcrop
from . import util
import os

# Initialize some environment variables
# TODO : check if the user has already defined these
os.environ['CRDS_SERVER_URL'] = 'https://hst-crds.stsci.edu'
os.environ['CRDS_PATH'] = os.path.abspath(os.path.join('.', 'reference_files'))
os.environ['iref'] = os.path.abspath(os.path.join('.', 'reference_files', 'references', 'hst', 'wfc3')) + os.path.sep
os.environ['jref'] = os.path.abspath(os.path.join('.', 'reference_files', 'references', 'hst', 'acs')) + os.path.sep

