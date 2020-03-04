"""
SOURCE:
    Mind of Douglas Adams

DESCRIPTION:
    Prints a nested object to the console in a human readable format

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
    None
"""
import json
#import Library_JsonLoad
import Library_NestedObjectNumpyElementsToLists

def Main(
    NestedObject = None,
    CheckArguments = True,
    PrintExtra = True,
    ):

    if (CheckArguments):
        ArgumentErrorMessage = ""

        if (NestedObject is None):
            ArgumentErrorMessage += "(NestedObject is None)" + "\n"

        if (len(ArgumentErrorMessage) > 0 ):
            if(PrintExtra):
                print("ArgumentErrorMessage:\n", ArgumentErrorMessage)
            raise Exception(ArgumentErrorMessage)


    #TODO: recursive search for numpy arrays -> cast those into 2d lists before jsonify
    PrettyPrintNestedObject = json.dumps(
        Library_NestedObjectNumpyElementsToLists.Main(
            NestedObject=NestedObject ,
            )        
        , indent=4)
    print(PrettyPrintNestedObject) 


















