"""
SOURCE:
    Mind of Douglas Adams
DESCRIPTION:
    Get the a monitor size on teh current computer.
    This will be used by graphing libraries to determin how many pixels are in the images.
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
    DummyArg
        Type:
            <class 'NoneType'>
        Description:
            None
RETURNS:
    Result
        Type:
        Description:
"""
#-------------------------------------------------------------------------------
def Main(
    DummyArg= None,
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

    Inch_in_Pixels = 80.0
    MonitorWidthPixels = 1920.0
    MonitorHeightPixels = 1080.0
    MonitorSize = (MonitorWidthPixels / Inch_in_Pixels,MonitorHeightPixels/Inch_in_Pixels)



    Result = MonitorSize
    return Result 
