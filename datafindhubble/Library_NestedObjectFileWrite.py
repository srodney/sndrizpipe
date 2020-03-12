"""
SOURCE:
    Mind of Douglas Adams
DESCRIPTION:
    Write a nested object to file
    Will use json format
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
    NestedObject
        Type:
            <class 'NoneType'>
        Description:
            None
    FilePath
        Type:
            <class 'NoneType'>
        Description:
            None
RETURNS:
    Result
        Type:
        Description:
"""
import json
import Library_FileWriteText
import Library_NestedObjectNumpyElementsToLists
#-------------------------------------------------------------------------------
def Main(
    NestedObject= None,
    FilePath= None,
    CheckArguments = True,
    PrintExtra = False,
    ):

    Result = None

    if (CheckArguments):
        ArgumentErrorMessage = ""

        if (len(ArgumentErrorMessage) > 0 ):
            if(PrintExtra):
                print("ArgumentErrorMessage:\n", ArgumentErrorMessage)
            raise Exception(ArgumentErrorMessage)


    NestedObjectString = json.dumps(
        Library_NestedObjectNumpyElementsToLists.Main(
            NestedObject=NestedObject ,
            )        , 
        indent=4)

    Result = Library_FileWriteText.Main(
        FilePath = FilePath,
        Text = NestedObjectString,
        OverWrite = True,
        )

    return Result 



















