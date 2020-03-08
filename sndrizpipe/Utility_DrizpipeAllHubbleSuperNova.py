
print ('starting pip imports...')
from sndrizpipe.runpipe_cmdline import runpipe
print('begining regular imports...')


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
print ('finished importing crap')

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
#Load found supernova catalog tables:
"""
shoes = Library_DataFileCsvReadAsAstropyTable.Main(
    Filepath= SuperNovaCatalogsDataDirectory + 'shoes.dat',
    ColumnNamesExisting= ['ID','redshift','RA','DEC', ],
    ColumnNamesNew= ['ID','z','ra','dec', ],
    )

pantheon = Library_DataFileCsvReadAsAstropyTable.Main(
    Filepath= SuperNovaCatalogsDataDirectory + 'pantheon.dat',
    ColumnNamesExisting= ['CID','zCMB','RA','DECL', 'PKMJD'],
    ColumnNamesNew= ['ID','z','ra','dec', 'mjd'],
    ColumnNamesRestrict = ['TYPE'],
    ColumnValuesRestrict = [0],
    )

raisin = Library_DataFileCsvReadAsAstropyTable.Main(
    Filepath= SuperNovaCatalogsDataDirectory + 'raisin.dat',
    ColumnNamesExisting= ['CID','zCMB','RA','DECL', 'PKMJD'],
    ColumnNamesNew= ['ID','z','ra','dec', 'mjd'],
    ColumnNamesRestrict = ['TYPE'],
    ColumnValuesRestrict = [0],
    )


Catalogs = [shoes, pantheon, raisin]
CatalogNames = ['shoes','pantheon', 'raisin']
"""

print ('Trying to extract meta data about the supernova')
MetaDataFileNames = os.listdir( SuperNovaMetaDataDirectory )[-3:]
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
    ProductListDirectory = os.path.realpath( SuperNovaImageDownloadDirectory + '/' +  FolderName + '/mastDownload' )
    ResultSymlinkDirectory = Library_BarbaraMikulskiArchiveSymlinkGroupMastDownloadDirectoryFiles.Main(
        ProductListDownloadDirectory= ProductListDirectory
        )
    SymlinkDirectories.append(ResultSymlinkDirectory)
    SymlinkDirectoryId = ResultSymlinkDirectory.split('/')[-2]
    SymlinkDirectoryIds.append(SymlinkDirectoryId)

    #Find the relevant row in the catalog:
    for MetaDataFileName in MetaDataFileNames:
        MetaDataFilePath = os.path.realpath( SuperNovaMetaDataDirectory + '/' + MetaDataFileName )
        print ('MetaDataFilePath', MetaDataFilePath)
        with open(MetaDataFilePath) as filehandle:
            MetaDataObject = json.load(filehandle)
        for ForSingleSuperNova in MetaDataObject:
            print ('ForSingleSuperNova')
            print (ForSingleSuperNova)
            if ForSingleSuperNova['ID'] == SymlinkDirectoryId:
                ra = ForSingleSuperNova['ra']
                dec = ForSingleSuperNova['dec']
                mjdmin = ForSingleSuperNova['mjd_range'][0]
                mjdmax =  ForSingleSuperNova['mjd_range'][1]
                ras.append(ra)
                decs.append(dec)
                mjdmins.append(mjdmin)
                mjdmaxs.append(mjdmax)
                break

print ('SymlinkDirectories', SymlinkDirectories)
print ('SymlinkDirectoryIds', SymlinkDirectoryIds)

"""
for SymlinkDirectory, ra, dec, mjdmin, mjdmax in zip(SymlinkDirectories, ras, decs, mjdmins, mjdmaxs):
    RunPipeArgumentDirectory = Library_StringFileNameStripLastExtension.Main(SymlinkDirectory)
    print ('RunPipeArgumentDirectory', RunPipeArgumentDirectory)


    #Change to the directory one level up from the symlink directory, so exposure.py works:
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
"""
