"""
SOURCE:
    Mind of Douglas Adams
DESCRIPTION:
    Creates a directory if a file path doesn't exist at the location
    If the directory does exist... then nothing happens.
    There is no overwrite option.
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
    Directory
        Type:
            <type 'NoneType'>
        Description:
RETURNS:
    Result
        Type:
        Description:
"""

import os

def Main(
    Directory = None,

    CheckArguments = True,
    PrintExtra = False,
    ):

    Result = False

    if (CheckArguments):
        ArgumentErrorMessage = ""

        if (len(ArgumentErrorMessage) > 0 ):
            if(PrintExtra):
                print("ArgumentErrorMessage:\n", ArgumentErrorMessage)
            raise Exception(ArgumentErrorMessage)

    Directory = os.path.realpath(Directory)
    if (not os.path.exists(Directory)):
        if (PrintExtra):
            print('Directory', Directory)
            print('Does not exist... Making directory now')
        try:
            os.makedirs(Directory)
        except Exception as ExceptionObject:
            print('Exception Encountered...')
            print('os.path.exists(Directory):', os.path.exists(Directory))
            print(str(ExceptionObject))
            print('Continuing...')
            pass

        Result = True

    return Result 















