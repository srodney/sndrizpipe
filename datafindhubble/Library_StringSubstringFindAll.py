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


RETURNS:

"""
import re

def Main(
    String = None,
    Substring = None,
    CheckArguments = True,
    PrintExtra = True,
    ):

    Result = None

    if (CheckArguments):
        ArgumentErrorMessage = ""

        if (None in [String, Substring]):
            ArgumentErrorMessage += "(None in [String, Substring])" + "\n"

        if (len(ArgumentErrorMessage) > 0 ):
            if(PrintExtra):
                print("ArgumentErrorMessage:\n", ArgumentErrorMessage)
            raise Exception(ArgumentErrorMessage)

    Result = [m.start() for m in re.finditer(Substring , String  )]

    return Result 














