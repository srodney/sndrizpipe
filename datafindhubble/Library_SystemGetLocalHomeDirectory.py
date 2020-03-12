"""
SOURCE:
    Mind of Douglas Adams
DESCRIPTION:
    Gets the local system home directory
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
RETURNS:
    Result
        Type:
        Description:
"""
#from os.path import expanduser


import os
import os.path


#-------------------------------------------------------------------------------
def Main(
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

    #Use the default os module to figure out the home directory:
    Result =  os.path.expanduser("~")

    #Check if you are in a docker container, and fix the result:
    if 'root' in Result:
        Result = '/home/user'

    return Result 






