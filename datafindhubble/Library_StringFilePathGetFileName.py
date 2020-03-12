"""
SOURCE:
    Mind of Douglas Adams
DESCRIPTION:
    Gets the filename out of a filepath
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
            <type 'NoneType'>
        Description:
RETURNS:
    Result
        Type:
        Description:
"""
def Main(
    FilePath = None,

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

    FilePathSplit = FilePath.split('/')
    Result = FilePathSplit[-1]

    return Result 














