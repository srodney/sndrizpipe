"""
SOURCE:
    https://stackoverflow.com/questions/21030391/how-to-normalize-an-array-in-numpy
DESCRIPTION:
    Normalize a numpy array.
    Do it fast.
    Use stack overflow
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
    NumpyArray
        Type:
            <class 'NoneType'>
        Description:
            None
    Axis
        Type:
            <class 'NoneType'>
        Description:
            None
    Order
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
    NumpyArray= None,
    Axis = -1,
    Order = 2,
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

    if False:
        l2 = numpy.atleast_1d(numpy.linalg.norm(NumpyArray, Order, Axis))
        l2[l2==0] = 1
        Result =  NumpyArray / numpy.expand_dims(l2, Axis)

    zmin = numpy.nanmin(NumpyArray) 
    zmax = numpy.nanmax(NumpyArray)
    zrng = zmax - zmin
    #print ('zmin', zmin)    
    #print ('zrng', zrng)

    zupshift = NumpyArray - zmin
    #print ('zupshift', zupshift)
    Result = zupshift / zrng
    return Result 




