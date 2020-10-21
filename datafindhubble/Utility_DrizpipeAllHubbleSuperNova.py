
print ('starting drizpipe imports...')
#from sndrizpipe.runpipe_cmdline import runpipe
#import runpipe_cmdline
import sndrizpipe
import sndrizpipe.runpipe_cmdline
print('begining regular imports...')
print ('\n\n\n')


import os
import sys
import astroquery
import astroquery.mast
import socket
import requests
import math
import sys
import pickle
import pprint
import warnings
import astropy
import astropy.io
import astropy.io.ascii
import astropy.table
import astroquery
import astroquery.mast 
import json
from pathlib import Path
#-------------------------------------------------------------------------------
sys.path.insert(1, '../datafindhubble')
import Library_AstropyDataTableSubsetOnColumnValues
import Library_SystemGetLocalHomeDirectory
import Library_SystemDirectoryCreateSafe
import Library_PrettyPrintNestedObject
import Library_NestedObjectFileWrite
import Library_DateStringNowGMT
import Library_DataFileCsvReadAsAstropyTable
import Library_PressTheAnyKey
import Library_ComponentExtract
import Library_DataFindBarbaraMikulskiArchiveProductsHubbleSingleObject
import Library_NestedObjectNumpyElementsToLists
import Library_SystemDirectoryCreateSafe
import Library_DataFindBarbaraMikulskiArchiveProductsHubbleSingleObject
import Library_PrettyPrintNestedObject
import Library_BarbaraMikulskiArchiveSymlinkGroupMastDownloadDirectoryFiles
import Library_StringFileNameStripLastExtension
import Library_BarbaraMikulskiArchiveSearchProductListMetaData
import Library_ComponentExtract
print ('finished all imports...')
print ('\n\n\n')

#-------------------------------------------------------------------------------
#Global settings for the run:
warnings.simplefilter('ignore')

#-------------------------------------------------------------------------------
#Directory Management:
HomeDirectory = Library_SystemGetLocalHomeDirectory.Main()
DataDirectory = HomeDirectory + '/DataHome'

HostName = socket.gethostname()
print ('HostName:', HostName)
if HostName == 'login001':
    DataDirectory = '/work/da2/DataHome'
print ('DataDirectory:' , DataDirectory)

SuperNovaCatalogsDataDirectory  = DataDirectory + '/AstronomySuperNovaData/SuperNovaCatalogs/'
SuperNovaImageDownloadDirectory = DataDirectory + '/AstronomySuperNovaData/SuperNovaHubbleImages/'
SuperNovaMetaDataDirectory      = DataDirectory + '/AstronomySuperNovaData/SuperNovaHubbleMetaData/'


#-------------------------------------------------------------------------------
#Get the supernova catalog meta data files for each catalog:
print ('Trying to extract meta data about the supernova')
MetaDataFileNames = list(sorted(os.listdir( SuperNovaMetaDataDirectory )))[-3:]
print ('MetaDataFileNames', MetaDataFileNames)
#-------------------------------------------------------------------------------



CurrentDirectory = os.getcwd()

#Get the list of directories for which we downloaded supernova data:
SuperNovaHubbleImageDirectories = os.listdir(SuperNovaImageDownloadDirectory) 

#For each supernova, get the symlink directory ( also try to create it, but it should exist already)
SymlinkDirectories = []
SymlinkDirectoryIds = []
ras = []
decs = []
mjdmins = []
mjdmaxs = []

for FolderName in SuperNovaHubbleImageDirectories:

    #Find the symlink directory
    ProductListDirectory = os.path.realpath( SuperNovaImageDownloadDirectory + '/' +  FolderName + '/mastDownload' )
    ResultSymlinkDirectory = Library_BarbaraMikulskiArchiveSymlinkGroupMastDownloadDirectoryFiles.Main(
        ProductListDownloadDirectory= ProductListDirectory
        )
    SymlinkDirectories.append(ResultSymlinkDirectory)
    SymlinkDirectoryId = ResultSymlinkDirectory.split('/')[-2]
    SymlinkDirectoryIds.append(SymlinkDirectoryId)

    #Find the relevant object in the meta data:
    FoundObjects = []
    for MetaDataFileName in MetaDataFileNames:
        MetaDataFilePath = os.path.realpath( SuperNovaMetaDataDirectory + '/' + MetaDataFileName )
        FoundObjects += Library_BarbaraMikulskiArchiveSearchProductListMetaData.Main(
            ProductListMetaDataFilePath = MetaDataFilePath,
            ConditionDictionary= {'ID': SymlinkDirectoryId }
            )
    SuperNovaObject = FoundObjects[0]

    #print ('SuperNovaObject', json.dumps(SuperNovaObject))


    #Store the stuff we need for the drizpipe to run with (from the meta data)
    ra = SuperNovaObject['ra']
    dec = SuperNovaObject['dec']

    mjdrange = Library_ComponentExtract.Main(
                Object          = SuperNovaObject,
                Key             = 'mjd_range',
                DefaultValue    = [None, None],  
                )
    if mjdrange is None:
        mjdrange = [None, None]

    print ('mjdrange', mjdrange)

    mjdmin = mjdrange[0]
    mjdmax = mjdrange[1]

    ras.append(ra)
    decs.append(dec)
    mjdmins.append(mjdmin)
    mjdmaxs.append(mjdmax)


print ('\n\n\n')
print('SymlinkDirectories', SymlinkDirectories )
print('SymlinkDirectoryIds', SymlinkDirectoryIds )
print('ras', ras )
print('decs', decs )
print('mjdmins', mjdmins )
print('mjdmaxs', mjdmaxs )


print ('len(SymlinkDirectories)', len(SymlinkDirectories))
print ('len(SymlinkDirectoryIds)', len(SymlinkDirectoryIds))
print ('len(ras)', len(ras))
print ('len(decs)', len(decs))
print ('len(mjdmins)', len(mjdmins))
print ('len(mjdmaxs)', len(mjdmaxs))


Indent = '    '
FailedIds = []
for SymlinkDirectory, SymlinkDirectoryId, ra, dec, mjdmin, mjdmax in zip(SymlinkDirectories, SymlinkDirectoryIds, ras, decs, mjdmins, mjdmaxs):
    print('Running sndrizpipe on the following parameters:')
    print(Indent, 'SymlinkDirectorie   ', SymlinkDirectory )
    print(Indent, 'SymlinkDirectoryId  ', SymlinkDirectoryId )
    print(Indent, 'ra                  ', ra )
    print(Indent, 'dec                 ', dec )
    print(Indent, 'mjdmin              ', mjdmin )
    print(Indent, 'mjdmax              ', mjdmax )

    RunPipeArgumentDirectory = Library_StringFileNameStripLastExtension.Main(SymlinkDirectory)
    #print ('RunPipeArgumentDirectory', RunPipeArgumentDirectory)
    print (Indent, 'RunPipeArgumentDirectory', RunPipeArgumentDirectory)

    #Change to the directory one level up from the symlink directory, so exposure.py works:
    path = Path(SymlinkDirectory)
    parent = path.parent
    os.chdir( parent )

    #Run the actual pipe command:
    os.environ["iref"] = ""
    os.environ["jref"] = ""
    os.environ["sig"] = ""

    try:
        if not None in [mjdmin, mjdmax]:
            sndrizpipe.runpipe_cmdline.runpipe(
                RunPipeArgumentDirectory, 
                ra = ra,
                dec = dec, 
                mjdmin = mjdmin,
                mjdmax = mjdmax,
                epochspan = 5,
                pixscale = 0.06,
                pixfrac = 0.8,
                doall=True, 
                tempepoch=1)
        else:
            sndrizpipe.runpipe_cmdline.runpipe(
                RunPipeArgumentDirectory, 
                ra = ra,
                dec = dec, 
                #mjdmin = mjdmin,
                #mjdmax = mjdmax,
                epochspan = 5,
                pixscale = 0.06,
                pixfrac = 0.8,
                doall=True, 
                tempepoch=1)
    except Exception as ExceptionObject:
        print (ExceptionObject)
        FailedIds.append(SymlinkDirectoryId)
        pass



    #Change back to the original directory after the pipe call is done
    os.chdir( CurrentDirectory )


print ('FailedIds', FailedIds)
print ('completed all drizzling.')






















