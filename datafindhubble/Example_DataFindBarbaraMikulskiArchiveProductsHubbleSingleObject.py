import Library_DataFindBarbaraMikulskiArchiveProductsHubbleSingleObject
import Library_PrettyPrintNestedObject

#Example from pantheon dataset:
"""
    "04D2al": {
        "productType": {
            "SCIENCE": 16
        },
        "dataproduct_type": {
            "image": 16
        },
        "proposal_id": {
            "9822": 16
        },
        "description": {
            "DADS FLT file - Calibrated exposure ACS/WFC3/STIS/COS": 16
        },
        "productDocumentationURL": {},
        "productSubGroupDescription": {
            "FLT": 16
        },
        "SingleSuperNovaRowCountFound": 4,
        "SingleSuperNovaProductCountFound": 16,
        "MJD": 53034.727,
        "RA": 150.468643,
        "DEC": 2.164106
    

    },

"""
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


print ('Starting a query for a single supernova object')
Result1 = Library_DataFindBarbaraMikulskiArchiveProductsHubbleSingleObject.Main(
    ObjectId                = "04D2al",
    ObjectRightAscension    = 150.468643,
    ObjectDeclination       =  2.164106,
    QueryRadius             = None,
    ObjectMjd               = 53034.727,
    QueryDateRange          = [
        53034.727 - 50, 
        53034.727 + 100],
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

print ('SingleObjectMetaData (pantheon supernova)')
Library_PrettyPrintNestedObject.Main(
    NestedObject= Result1['SingleObjectMetaData'],
    )
#pprint.pprint( Result['SingleObjectMetaData'] ) 

print ('SingleObjectProductListTable (pantheon supernova)')
print( Result1['SingleObjectProductListTable'] ) 




"""
"MACS J002523.4-121942": {
        "DownloadMetaData": {
            "productType": {
                "SCIENCE": 40
            },
            "dataproduct_type": {
                "image": 40
            },
            "proposal_id": {
                "14096": 4,
                "10703": 24,
                "9722": 12
            },
            "description": {
                "DADS FLT file - Calibrated exposure ACS/WFC3/STIS/COS": 40
            },
            "productDocumentationURL": {},
            "productSubGroupDescription": {
                "FLT": 40
            }
        },
        "ra": 6.3479305559,
        "dec": -12.3286802225,
        "productcount": 40,
        "filters": [
            "F555W;CLEAR2L",
            "CLEAR1L;F814W",
            "F555W;CLEAR2L",
            "CLEAR1L;F814W",
            "F555W;CLEAR2L",
            "CLEAR1L;F814W",
            "CLEAR1L;F435W",
            "F450W",
            "F450W",
            "F450W",
            "F450W",
            "F450W",
            "F450W",
            "F450W",
            "F450W",
            "F450W",
            "F450W",
            "F555W",
            "F814W",
            "F814W;F555W",
            "DETECTION",
            "F814W;F555W",
            "F555W",
            "DETECTION",
            "F814W",
            "F435W",
            "DETECTION",
            "F450W",
            "DETECTION"
        ],
        "catalog": "master"
    },


"""




print ('\n\n\n\n')


print ('Starting a query for a lense-thingy object')
Result2 = Library_DataFindBarbaraMikulskiArchiveProductsHubbleSingleObject.Main(
    ObjectId                = "MACS J002523.4-121942",
    ObjectRightAscension    = 6.3479305559,
    ObjectDeclination       = -12.3286802225,
    QueryRadius             = None,
    ObjectMjd               = None,
    QueryDateRange          = None,
    QuerySubsetColumnNames  = [
        'instrument_name',
        #'filters',
        'obs_collection',
        ],
    QuerySubsetColumnsValuesOfInterest = [
        AllowedInstruments, 
        #AllowedFilters,
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
    ObjectSourceCatalog = 'masterlens',
    ResultFormat            = 'Dictionary',
    )

print ('SingleObjectMetaData (masterlens lense object )')
Library_PrettyPrintNestedObject.Main(
    NestedObject= Result2['SingleObjectMetaData'],
    )
#pprint.pprint( Result['SingleObjectMetaData'] ) 

print ('SingleObjectProductListTable (masterlens lense object )')
print( Result2['SingleObjectProductListTable'] ) 








#What if I want to actually download the image product list for the object?
"""
SingleObjectDownloadDirectory = '/pathtodownload'

astroquery.mast.Observations.download_products(
    SingleObjectProductListTable,
    download_dir = SingleObjectDownloadDirectory,
    cache = True,
    )
"""
























