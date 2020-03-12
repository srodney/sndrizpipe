"""
SOURCE:
    Mind of Douglas Adams
DESCRIPTION:
    Get the subset of an astropy datatable 
    for which all values of a particular column, 
    are in a list of values of interest. 
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
    AstropyDataTable
        Type:
            <class 'NoneType'>
        Description:
            None
    ColumnName
        Type:
            <class 'NoneType'>
        Description:
            None
    ColumnValuesOfInterest
        Type:
            <class 'NoneType'>
        Description:
            None
RETURNS:
    Result
        Type:
        Description:
"""
#-------------------------------------------------------------------------------
def Main(
    AstropyDataTable= None,
    ColumnName= None,
    ColumnNames= None,
    ColumnValuesOfInterest= None,
    ColumnsValuesOfInterest= None,
    CheckArguments = True,
    PrintExtra = False,
    ):

    Result = None

    if (CheckArguments):
        ArgumentErrorMessage = ""

        SingleSelectionArgSetPassed = (ColumnName is not None) and (ColumnValuesOfInterest is not None)
        MultiSelectionArgSetPassed = (ColumnNames is not None) and (ColumnsValuesOfInterest is not None)

        if SingleSelectionArgSetPassed and MultiSelectionArgSetPassed:
            ArgumentErrorMessage += 'SingleSelectionArgSetPassed and MultiSelectionArgSetPassed \n'

        if not SingleSelectionArgSetPassed and not MultiSelectionArgSetPassed:
            ArgumentErrorMessage += 'not SingleSelectionArgSetPassed and not MultiSelectionArgSetPassed \n'

        if (len(ArgumentErrorMessage) > 0 ):
            if(PrintExtra):
                print("ArgumentErrorMessage:\n", ArgumentErrorMessage)
            raise Exception(ArgumentErrorMessage)

    #Allow access to "bad" values. Astropy calls them 'masked' values.
    AstropyDataTable = AstropyDataTable.filled()

    #Python list comprehension creates a list of true false values on the column:    
    Mask = None
    if SingleSelectionArgSetPassed:
        Mask = [Item in ColumnValuesOfInterest for Item in AstropyDataTable[ColumnName] ]



    elif MultiSelectionArgSetPassed:
        Mask = [True for Item in AstropyDataTable ]

        for ColumnName, ColumnValuesOfInterest in zip(ColumnNames, ColumnsValuesOfInterest):

            #Create a mask for a single column:
            SingleColumnMask = [Item in ColumnValuesOfInterest for Item in AstropyDataTable[ColumnName] ]
            #$print ('SingleColumnMask', SingleColumnMask)

            #Perform elementwise "AND" on the single column, and the running final mask
            Mask = [ Item1 and Item2 for Item1, Item2 in zip(Mask, SingleColumnMask ) ]

    if PrintExtra: print ('Mask', Mask)

    #Astropy returns a subset of rows absed on the list of true false values:
    Result = AstropyDataTable[Mask]         

    return Result 





























