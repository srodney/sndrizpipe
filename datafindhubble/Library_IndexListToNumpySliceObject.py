"""
SOURCE:
    Mind of Douglas Adams
DESCRIPTION:
    Takes a list of indices
    does stupid manipulation
    returns the transposed, tupled version
    which can be thrown into a numpy array to get back out values.
    avoiding for loops is the reason for this library
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
    IndexList
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
#-------------------------------------------------------------------------------
def Main(
    IndexList= None,
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



    NumpySliceObject = tuple( numpy.array(IndexList).T.tolist() )

    Result = NumpySliceObject
    return Result 












