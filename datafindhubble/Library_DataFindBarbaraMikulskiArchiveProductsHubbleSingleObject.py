"""
SOURCE:
    Mind of Douglas Adams
DESCRIPTION:
    Goes to the astroquery mast archive.
    Gets all the images which satisfy the following conditions:
    Is a hubble image
    Its from one of the allowed instruments
    Is within one of the allowed filters. 
ARGS:
    CheckArguments
        Type:
            python boolean
        Description:
            if true, checks the arguments with conditions written in the function
            if false, ignores those conditions
    PrintExtra
        Type:
            python integer
        Description:
            if greater than 0, prints addional information about the function
            if 0, function is expected to print nothing to console
            Additional Notes:
                The greater the number, the more output the function will print
                Most functions only use 0 or 1, but some can print more depending on the number
    ObjectId
        Type:
            <class 'NoneType'>
        Description:
            None
    ObjectRightAscension
        Type:
            <class 'NoneType'>
        Description:
            None
    ObjectDeclination
        Type:
            <class 'NoneType'>
        Description:
            None
    QueryRadius
        Type:
            <class 'NoneType'>
        Description:
            None
    QuerySubsetColumnNames
        Type:
            <class 'NoneType'>
        Description:
            None
    QuerySubsetColumnsValuesOfInterest
        Type:
            <class 'NoneType'>
        Description:
            None
    QueryDateRange
        Type:
            <class 'list'> of <class 'float'>
        Description:
            Minimum and maximum "modified julian dates"
            [min_mjd, max_mjd]

    ProductSubsetType
        Type:
            <class 'NoneType'>
        Description:
            None
    ProductSubsetSubGroupDescription
        Type:
            <class 'NoneType'>
        Description:
            None
    ProductSubsetExtension
        Type:
            <class 'NoneType'>
        Description:
            None

    ResultFormat
        Type:
            <class 'NoneType'>
        Description:
            None
RETURNS:
    Result
        Type:
        Description:
"""
import astroquery
import astroquery.mast 
import Library_BarbaraMikulskiArchiveQueryRegion
import Library_BarbaraMikulskiArchiveCollectProductListMetaData
#-------------------------------------------------------------------------------
def Main(
    ObjectSourceCatalog = None,
    ObjectId= None,
    ObjectRightAscension= None,
    ObjectDeclination= None,
    ObjectMjd= None,

    QueryRadius= None,
    QueryDateRange = None,

    QuerySubsetColumnNames= None,
    QuerySubsetColumnsValuesOfInterest= None,

    ProductSubsetColumnNames = None,
    ProductSubsetColumnsValuesOfInterest = None,
    #ProductSubsetType= None,
    #ProductSubsetSubGroupDescription= None,
    #ProductSubsetExtension= None,

    ResultFormat= None,
    CheckArguments = True,
    PrintExtra = False,
    ):

    Result = None

    if not (QueryDateRange is None):
        QueryDataLower = QueryDateRange[0]
        QueryDataUpper = QueryDateRange[1]

    if (CheckArguments):
        ArgumentErrorMessage = ""

        if (len(ArgumentErrorMessage) > 0 ):
            if(PrintExtra):
                print("ArgumentErrorMessage:\n", ArgumentErrorMessage)
            raise Exception(ArgumentErrorMessage)


    #Perform an initial query based on the location information:
    SingleObjectQueryResult = Library_BarbaraMikulskiArchiveQueryRegion.Main(
        RightAscension= ObjectRightAscension,
        Declination= ObjectDeclination,
        Radius=  QueryRadius,
        SubsetColumnNames = QuerySubsetColumnNames,
        SubsetColumnsValuesOfInterest = QuerySubsetColumnsValuesOfInterest,
        )
    if PrintExtra:
        print ('SingleObjectQueryResult')
        print (SingleObjectQueryResult)



    #Further subsetify based on the mjd (modified julian date):
    if not (QueryDateRange is None):
        ModifiedJulianDateMask = [ ]
        for Row in SingleObjectQueryResult:
            LowerBoundSatisfied = ( QueryDataLower < Row['t_min'] ) 
            UpperBoundSatisfied = ( Row['t_min'] < QueryDataUpper )
            ModifiedJulianDateMask.append(LowerBoundSatisfied and UpperBoundSatisfied)
        SingleObjectQueryResult = SingleObjectQueryResult[ModifiedJulianDateMask]
    if PrintExtra:
        print ('SingleObjectQueryResult (date criterion subset)')
        print (SingleObjectQueryResult)



    #Get a list of available filters for the query:
    AvailableFilters = list(SingleObjectQueryResult['filters'])
    if PrintExtra:
        print ('AvailableFilters')
        print (AvailableFilters)



    #Get the product list
    SingleObjectProductListTable =  astroquery.mast.Observations.get_product_list( 
        SingleObjectQueryResult
        )
    if PrintExtra:
        print ('SingleObjectProductListTable')
        print (SingleObjectProductListTable)



    #Filter the product list             
    #   https://mast.stsci.edu/api/v0/_productsfields.html
    #   The ugly "dictionary unpacking into args" is required because of bad astroquery code design   
    #   https://stackoverflow.com/questions/334655/passing-a-dictionary-to-a-function-as-keyword-parameters
    SingleObjectProductListTable = astroquery.mast.Observations.filter_products(
        SingleObjectProductListTable,
        **dict(zip(ProductSubsetColumnNames, ProductSubsetColumnsValuesOfInterest ))
        )
    if PrintExtra:
        print ('SingleObjectProductListTable (product criterion subset)')
        print (SingleObjectProductListTable)


    #Count how many images (products) we found 
    ProductCount = len(SingleObjectProductListTable)
    if PrintExtra:
        print ('ProductCount')
        print (ProductCount)


    #Construct a "product-metadata python-object" about the "sky-object":
    SingleObjectProductListMetaData = Library_BarbaraMikulskiArchiveCollectProductListMetaData.Main(
        SingleObjectProductListTable = SingleObjectProductListTable,
        ProductColumnNames = [
            "productType",
            "dataproduct_type",
            "proposal_id",
            "description",
            "productDocumentationURL",
            "productSubGroupDescription",
            ],
        )
    if PrintExtra:
        print ('SingleObjectProductListMetaData')
        print (SingleObjectProductListMetaData)


    #Construct the "metadata python-object" about the "sky-object"   
    SingleObjectMetaData = {}
    SingleObjectMetaData['DownloadMetaData']    = SingleObjectProductListMetaData
    SingleObjectMetaData['ra']                  = ObjectRightAscension
    SingleObjectMetaData['dec']                 = ObjectDeclination
    SingleObjectMetaData['mjd']                 = ObjectMjd
    SingleObjectMetaData['mjd_range']           = QueryDateRange
    SingleObjectMetaData['productcount']        = ProductCount
    SingleObjectMetaData['filters']             = AvailableFilters
    SingleObjectMetaData['catalog']             = ObjectSourceCatalog
    SingleObjectMetaData['ID']                  = ObjectId

    if ResultFormat is 'Dictionary':
        Result = {
            "SingleObjectMetaData": SingleObjectMetaData,
            "SingleObjectProductListTable": SingleObjectProductListTable
            }
    else:
        Result = SingleObjectProductListTable


    return Result 








