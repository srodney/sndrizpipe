"""
SOURCE:
    Mind of Douglas Adams
DESCRIPTION:
    Collects metadata about images we could download into a single object
    without actually downloading
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
    SingleObjectProductListTable
        Type:
            <class 'NoneType'>
        Description:
            astroquery.mast.Observations.get_product_list(
    SingleObjectArchiveData
        Type:
            <class 'NoneType'>
        Description:
            Library_BarbaraMikulskiArchiveQueryRegion

    ProductColumnNames
        Type:
            <class 'NoneType'>
        Description:
            None

    AllowedProducts

RETURNS:
    Result
        Type:
        Description:
"""
import astroquery
import astroquery.mast 
import Library_AstropyDataTableSubsetOnColumnValues
#-------------------------------------------------------------------------------
def Main(
    SingleObjectProductListTable= None,
    SingleObjectArchiveData = None,
    ProductColumnNames= None,

    AllowedProducts = None,

    CheckArguments = True,
    PrintExtra = False,
    ):

    Result = None

    if (CheckArguments):
        ArgumentErrorMessage = ""

        if len(set(ProductColumnNames)) != len(ProductColumnNames):
            ArgumentErrorMessage += 'column names not set'

        if (len(ArgumentErrorMessage) > 0 ):
            if(PrintExtra):
                print("ArgumentErrorMessage:\n", ArgumentErrorMessage)
            raise Exception(ArgumentErrorMessage)


    #Get the product list
    if (SingleObjectProductListTable is None) and (SingleObjectArchiveData is not None):
        SingleObjectProductListTable =  astroquery.mast.Observations.get_product_list( 
            SingleObjectArchiveData 
            )

    #Filter the product list
    #       https://mast.stsci.edu/api/v0/_productsfields.html
    if AllowedProducts is not None:
        SingleObjectProductListTable = astroquery.mast.Observations.filter_products(
            SingleObjectProductListTable,
            productType = AllowedProducts['productType'],
            productSubGroupDescription = AllowedProducts['productSubGroupDescription'],
            extension=AllowedProducts['extension'],
            )

    def CollectCountingMetaDataOnColumnName( 
        ProductListTable = None ,
        ColumnName = None,
        ):
        ColumnPossibleValues = list(set(ProductListTable[ColumnName]._data))
        if PrintExtra: print ('ColumnPossibleValues', ColumnPossibleValues)
        StupidValueList = ['', None]

        ColumnPossibleValueCounts = {}
        for ColumnPossibleValue in ColumnPossibleValues:
            if not (ColumnPossibleValue in StupidValueList):
                try:
                    ColumnPossibleValueCount = len(Library_AstropyDataTableSubsetOnColumnValues.Main(
                        AstropyDataTable = ProductListTable,
                        ColumnName= ColumnName,
                        ColumnValuesOfInterest = ColumnPossibleValue,
                        ))
                except:
                    print ('New stupid value found')
                    print ('ProductListTable', list(ProductListTable[ColumnName]))
                    print ('ColumnName', ColumnName)
                    print ('ColumnPossibleValue', ColumnPossibleValue)
                    raise Exception('')
                ColumnPossibleValueCounts[ColumnPossibleValue] = ColumnPossibleValueCount
        return ColumnPossibleValueCounts

    MetaData = {}
    for ColumnName in ProductColumnNames:
        ColumnNameMetaData = CollectCountingMetaDataOnColumnName(
            ProductListTable = SingleObjectProductListTable ,
            ColumnName = ColumnName,
            )
        MetaData[ColumnName] = ColumnNameMetaData
    
    Result = MetaData
    return Result 













