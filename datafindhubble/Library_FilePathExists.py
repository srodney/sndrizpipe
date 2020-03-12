
"""
SOURCE:
    None

DESCRIPTION:

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
            python string
        Description:
            The filepath on which to ccheck existence
        

RETURNS:

    True on existence
    False on lack of existence

"""
import os
def Main(
    FilePath = None,
    CheckArguments = True,
    PrintExtra = True,
    ):

    FileExists = False

    if (CheckArguments):
        ArgumentErrorMessage = ""

        if (FilePath is None):
            ArgumentErrorMessage += "(FilePath is None)" + "\n"

        if (len(ArgumentErrorMessage) > 0 ):
            if(PrintExtra):
                print("ArgumentErrorMessage:\n", ArgumentErrorMessage)
            raise Exception(ArgumentErrorMessage)


    FileExists = os.path.exists(FilePath)


    return FileExists


















