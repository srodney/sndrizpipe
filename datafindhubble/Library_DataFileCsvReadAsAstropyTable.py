"""
SOURCE:
    Mind of Douglas Adams
DESCRIPTION:
    Reads in a CSV file with a path
    Turns it into an astropy table
    Maps a set of existing column names
    To a set of new columns
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
    Filepath
        Type:
            <class 'NoneType'>
        Description:
            None
    ColumnNamesExisting
        Type:
            <class 'NoneType'>
        Description:
            None
    ColumnNamesNew
        Type:
            <class 'NoneType'>
        Description:
            None
RETURNS:
    Result
        Type:
        Description:
"""
import numpy
import pandas
import astropy
import astropy.table
import astropy.io
#-------------------------------------------------------------------------------
def Main(
    Filepath= None,
    ColumnNamesExisting= None,
    ColumnNamesNew= None,
    ColumnNamesRestrict = None,
    ColumnValuesRestrict = None,
    ResultFormat = None,
    CheckArguments = True,
    PrintExtra = False,
    ):

    if ResultFormat is None:
        ResultFormat = 'astropy'

    Result = None

    if ColumnNamesRestrict is None:
        ColumnNamesRestrict = []

    if ColumnValuesRestrict is None:
        ColumnValuesRestrict = []

    if (CheckArguments):
        ArgumentErrorMessage = ""

        if (len(ArgumentErrorMessage) > 0 ):
            if(PrintExtra):
                print("ArgumentErrorMessage:\n", ArgumentErrorMessage)
            raise Exception(ArgumentErrorMessage)

    #Load table in astropy format regardless of header types:
    AstropyTableFull = None
    try:
        AstropyTableFull = astropy.io.ascii.read(Filepath)
    except:    
        PandasTableFull = pandas.read_csv(Filepath)
        PandasTableFull = PandasTableFull.rename(columns=lambda x: x.strip())
        AstropyTableFull = astropy.table.Table.from_pandas(PandasTableFull)


    #Take the subset of the table which satisfies the resistrictions
    AstropyTableSubset = AstropyTableFull
    for ColumnNameRestrict, ColumnValueRestrict in zip(ColumnNamesRestrict, ColumnValuesRestrict):
        AstropyTableSubset = AstropyTableSubset[AstropyTableSubset[ ColumnNameRestrict ]==ColumnValueRestrict]
    if PrintExtra: 
        print ('AstropyTableSubset[:10]', AstropyTableSubset[:10])
        print ('AstropyTableSubset.colnames')
        print (AstropyTableSubset.colnames)


    #Make a data object containing a list of the columns we want
    ColumnsWanted = []
    for ColumnNameExisting in ColumnNamesExisting:
        SingleColumn = AstropyTableFull[ColumnNameExisting]
        if PrintExtra > 1: print ('SingleColumn', SingleColumn)
        ColumnsWanted.append(SingleColumn)
    if PrintExtra: 
        print ('ColumnsWanted', ColumnsWanted)


    #Use astropy to map the data in the columns to new names in a new table
    AstropyTableSubsetColumnMap = astropy.table.Table(
        ColumnsWanted,
        names=ColumnNamesNew
        )
    if ResultFormat is 'astropy':
        Result = AstropyTableSubsetColumnMap
    elif ResultFormat is 'numpy':
        ColumnNames = AstropyTableSubsetColumnMap.colnames
        #Result = numpy.array(AstropyTableSubsetColumnMap).tolist()
        #Result = numpy.array([*Result]).astype(numpy.float)


    return Result 























