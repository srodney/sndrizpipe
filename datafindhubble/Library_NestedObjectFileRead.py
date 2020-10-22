"""
SOURCE:
    Mind of Douglas Adams
DESCRIPTION:
    Read a filepath into a nested python object 
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
import Library_FileReadAsText
import Library_JsonLoad
#-------------------------------------------------------------------------------
def Main(
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

    #Read in the contents of the original file into a python object:
    OriginalContents = Library_FileReadAsText.Main( FilePath )
    NestedObject =  Library_JsonLoad.Main(OriginalContents)

    Result = NestedObject
    return Result 
