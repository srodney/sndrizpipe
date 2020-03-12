__author__ = 'douglasquincyadams'

# TODO : add a test that uses the command-line interface
# command-line test :
# sndrizzle --filters F160W  --doall --mjdmin 56010 --mjdmax 56300 --ra 189.156538 --dec 62.309147  --refcat 'goodsn_mosaic.cat' colfax

import os
import os
import sys
import astroquery
import astroquery.mast
from sndrizpipe.runpipe_cmdline import runpipe



sys.path.insert(1, '../datafindhubble')

import Library_StringFileNameStripLastExtension
import Library_SystemDirectoryCreateSafe
import Library_DataFindBarbaraMikulskiArchiveProductsHubbleSingleObject
import Library_PrettyPrintNestedObject
import Library_BarbaraMikulskiArchiveSymlinkGroupMastDownloadDirectoryFiles


#Create a new directory to store hubble data in:
Library_SystemDirectoryCreateSafe.Main('hubbledownloadtestdata')


#Subselection Criterion for the super nova arhive data:
AllowedFilters=[
    'F606W',
    'F625W',
    'F775W',
    'F814W',
    'F850LP',
    'F105W',
    'F110W',
    'F125W',
    'F140W',
    'F160W',
    ]

AllowedInstruments=[
    'WFPC2/WFC',
    'PC/WFC',
    'ACS/WFC',
    'ACS/HRC',
    'ACS/SBC',
    'WFC3/UVIS',
    'WFC3/IR'
    ]

AllowedCollections = [
    'HLA',
    'HST'
    ]

SubsetColumnNames = [
    'instrument_name',
    'filters',
    'obs_collection',
    ]

SubsetColumnsValuesOfInterest = [
    AllowedInstruments, 
    AllowedFilters,
    AllowedCollections,
    ]


#Go get the product list for a single supernova we are going to test:
print ('Starting a query for a single supernova object')
Result1 = Library_DataFindBarbaraMikulskiArchiveProductsHubbleSingleObject.Main(
    ObjectId                = "04D2al",
    ObjectRightAscension    = 150.468643,
    ObjectDeclination       =  2.164106,
    QueryRadius             = None,
    ObjectMjd               = 53034.727,
    QueryDateRange          = [
        53034.727 - 50,   #52984.727
        53034.727 + 100], #53134.727
    QuerySubsetColumnNames  = [
        'instrument_name',
        'filters',
        'obs_collection',
        ],
    QuerySubsetColumnsValuesOfInterest = [
        AllowedInstruments, 
        AllowedFilters,
        AllowedCollections,
        ],
    ProductSubsetColumnNames = [
        'productType',
        'productSubGroupDescription',
        'extension',
        ],
    ProductSubsetColumnsValuesOfInterest = [
        ["SCIENCE"],
        ["FLT"],
        ["fits"],
        ],
    ObjectSourceCatalog = 'pantheon',
    ResultFormat            = 'Dictionary',
    )
TestSupernovaProductListMetaData = Result1['SingleObjectMetaData']
TestSupernovaProductListTable = Result1['SingleObjectProductListTable']


print ('SingleObjectMetaData (pantheon supernova)')
Library_PrettyPrintNestedObject.Main( NestedObject= TestSupernovaProductListMetaData )


print ('SingleObjectProductListTable (pantheon supernova)')
print( TestSupernovaProductListTable ) 


#Do the download of the test supernova dtaa
astroquery.mast.Observations.download_products(
    TestSupernovaProductListTable,
    download_dir = './hubbledownloadtestdata',
    cache = True,
    )

#Create a symlink directory to the all the fits files just downloaded
SymlinkDirectory = Library_BarbaraMikulskiArchiveSymlinkGroupMastDownloadDirectoryFiles.Main(
        ProductListDownloadDirectory= './hubbledownloadtestdata/mastDownload'
        )

print ('SymlinkDirectory', SymlinkDirectory)

TestCommand = "sndrizpipe --ra 150.468643 --dec 2.164106 --mjdmin 52984.727 --mjdmax 53134.727 --epochspan 5 --pixscale 0.06 --pixfrac 0.8 --doall --tempepoch 1 " + SymlinkDirectory
print ('TestCommand')
print (TestCommand)




print ("Trying to run the test command, without opening a shell.")
print ("Instead we will call the `sndrizpipe.runpipe_cmdline.runpipe` command")

RunPipeArgumentDirectory = Library_StringFileNameStripLastExtension.Main(SymlinkDirectory)
print ('RunPipeArgumentDirectory', RunPipeArgumentDirectory)



CurrentDirectory = os.getcwd()

#Change to the directory one level up from the symlink directory, so exposure.py works:
from pathlib import Path
path = Path(SymlinkDirectory)
parent = path.parent
os.chdir( parent )

#Run the actual pipe command:
os.environ["iref"] = ""
os.environ["jref"] = ""
runpipe(
    RunPipeArgumentDirectory, 
    ra = 150.468643,
    dec = 2.164106, 
    mjdmin = 52984.727,
    mjdmax = 53134.727,
    epochspan = 5,
    pixscale = 0.06,
    pixfrac = 0.8,
    doall=True, 
    tempepoch=1)

#Change back to the original directory after the pipe call is done
os.chdir( CurrentDirectory )








