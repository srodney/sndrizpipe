"""
    SOURCE: 
        https://astroquery.readthedocs.io/en/latest/mast/mast.html
        https://mast.stsci.edu/api/v0/_c_a_o_mfields.html
        https://mast.stsci.edu/api/v0/_productsfields.html
    DESCRIPTION: 
        This module can be used to query 
        the Barbara A. Mikulski Archive for Space Telescopes (MAST). 

        astroquery.mast.Observations.query_region
"""
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
#-------------------------------------------------------------------------------
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
import Library_SystemGetLocalDataDirectory

#-------------------------------------------------------------------------------
#Global settings for the run:
warnings.simplefilter('ignore')
PrintExtra = False
DoDownload = True
DownloadItemMaximum = 1000

#-------------------------------------------------------------------------------
#Directory Management:
HomeDirectory = Library_SystemGetLocalHomeDirectory.Main()
DataDirectory = Library_SystemGetLocalDataDirectory.Main()

SuperNovaCatalogsDataDirectory  = DataDirectory + '/AstronomySuperNovaData/SuperNovaCatalogs/'
SuperNovaImageDownloadDirectory = DataDirectory + '/AstronomySuperNovaData/SuperNovaHubbleImages/'
SuperNovaMetaDataDirectory      = DataDirectory + '/AstronomySuperNovaData/SuperNovaHubbleMetaData/'


#-------------------------------------------------------------------------------
#Load found supernova catalog tables:
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
#-------------------------------------------------------------------------------
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


DownloadItemCount = 0

for Catalog, CatalogName in zip(Catalogs, CatalogNames):

    print ('CatalogName:', CatalogName)
    SingleCatalogAllObjectsMetaData = []
    for SingleSuperNova in Catalog[:30]:
        #print ('SingleSuperNova', SingleSuperNova)


        #Extract the MJD, and corresponding date range to query from hubble.
        #   If none is found in the catalog, then search hubble for ALL TIME
        SingleSuperNovaMJD = Library_ComponentExtract.Main( 
            Object          = SingleSuperNova,
            Key             = 'mjd' ,
            DefaultValue    = None,
            )
        if SingleSuperNovaMJD is None:
            SingleSuperNovaDateRange = None
        else:
            SingleSuperNovaDateRange = [
                SingleSuperNova['mjd'] - 50, 
                SingleSuperNova['mjd'] + 100
                ]

        #Query the archive for what files exist given the constraints:
        ProductListResult = Library_DataFindBarbaraMikulskiArchiveProductsHubbleSingleObject.Main(
            ObjectId                = SingleSuperNova['ID'],
            ObjectRightAscension    = SingleSuperNova['ra'],
            ObjectDeclination       = SingleSuperNova['dec'],
            QueryRadius             = None, #defaults to 0.03
            ObjectMjd               = SingleSuperNovaMJD,
            QueryDateRange          = SingleSuperNovaDateRange,
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
            ObjectSourceCatalog     = CatalogName,
            ResultFormat            = 'Dictionary',
            )
        SingleObjectMetaData = ProductListResult['SingleObjectMetaData']
        SingleObjectProductListTable = ProductListResult['SingleObjectProductListTable']
        SingleCatalogAllObjectsMetaData.append(SingleObjectMetaData)


        #Do type checking in the product result list:
        try:
            json.dumps(
                Library_NestedObjectNumpyElementsToLists.Main(
                            NestedObject=SingleObjectMetaData ,
                            ) )
        except Exception as ExpectionObject:
            print ('SingleObjectMetaData not json serializable')
            print (SingleObjectMetaData)
            print ('ExpectionObject')
            print (ExpectionObject)

        #Actually perform the download operation
        SingleSuperNovaProductCount = int(SingleObjectMetaData['productcount']) 
        print (SingleObjectMetaData['ID'], ' has: ', SingleSuperNovaProductCount, ' files available for download')


        #Create a download directory for the supernova
        SingleSuperNovaDownloadDirectory = SuperNovaImageDownloadDirectory 
        SingleSuperNovaDownloadDirectory +=  '/' + str(SingleSuperNova['ID'])
        if SingleSuperNovaProductCount > 0:
            Library_SystemDirectoryCreateSafe.Main( Directory = SingleSuperNovaDownloadDirectory )

        #Perform the download and get hubble images onto disk
        if DoDownload and SingleSuperNovaProductCount > 0:
            print ('Starting Download...')
            astroquery.mast.Observations.download_products(
                SingleObjectProductListTable,
                download_dir = SingleSuperNovaDownloadDirectory,
                cache = True,
                )
            DownloadItemCount += SingleSuperNovaProductCount 

        #Check if we exeeded the maximum number of hubble images we want to download for the run
        if DownloadItemCount > DownloadItemMaximum:
            print ('Maximum download count exceeded. Stopping')
            break


    #Store the meta data for all the objects  
    SingleCatalogMetaDataStorageFilePath =  SuperNovaMetaDataDirectory 
    SingleCatalogMetaDataStorageFilePath += '/' +  Library_DateStringNowGMT.Main() 
    SingleCatalogMetaDataStorageFilePath += '_MetaData_' + CatalogName + '.txt'
    Library_NestedObjectFileWrite.Main(
        NestedObject    = SingleCatalogAllObjectsMetaData,
        FilePath        = SingleCatalogMetaDataStorageFilePath,
        )
    



print ('Finishing.')
print ('DownloadItemCount:', DownloadItemCount)















































