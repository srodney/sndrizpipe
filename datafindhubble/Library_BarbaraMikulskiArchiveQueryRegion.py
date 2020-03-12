"""
SOURCE:
    Mind of Douglas Adams
DESCRIPTION:
    Queries the astro mast archive
    using an ra, dec, radius
    returns a result table
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
    RightAscension
        Type:
            <class 'NoneType'>
        Description:
            None
    Declination
        Type:
            <class 'NoneType'>
        Description:
            None
    Radius
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
import Library_AstropyDataTableSubsetOnColumnValues
#-------------------------------------------------------------------------------
def Main(
    RightAscension= None,
    Declination= None,
    Radius= None,

    SubsetColumnNames = None,
    SubsetColumnsValuesOfInterest = None,


    CheckArguments = True,
    PrintExtra = False,
    ):

    Result = None

    DoSubset = (SubsetColumnNames is not None) and (SubsetColumnsValuesOfInterest is not None)

    if (CheckArguments):
        ArgumentErrorMessage = ""

        if DoSubset and len(SubsetColumnNames) != len(SubsetColumnsValuesOfInterest):
            ArgumentErrorMessage += 'len(SubsetColumnNames) != len(SubsetColumnsValuesOfInterest)'


        if (len(ArgumentErrorMessage) > 0 ):
            if(PrintExtra):
                print("ArgumentErrorMessage:\n", ArgumentErrorMessage)
            raise Exception(ArgumentErrorMessage)

    if Radius is None:
        Radius = 0.03


    try:
        RightAscension = str(RightAscension)
        Declination = str(Declination)
        Radius = str(Radius)
    except:
        raise Exception('Unable to cast args to strings. Check datatypes')


    #ICRS coordinate provided in degrees
    PositionString = RightAscension + " "+ Declination


    #Perform the query
    ArchiveData = astroquery.mast.Observations.query_region(
        PositionString,
        radius = Radius + " deg"
        )



    #Take a subset of the archive based on insturment, Subset, and collection requirements:
    ArchiveDataSubset = ArchiveData


    if DoSubset and len(ArchiveData) > 0:
        ArchiveDataSubset = Library_AstropyDataTableSubsetOnColumnValues.Main(
            AstropyDataTable = ArchiveData,
            ColumnNames= SubsetColumnNames,
            ColumnsValuesOfInterest= SubsetColumnsValuesOfInterest,
            )



    Result = ArchiveDataSubset
    return Result 
















