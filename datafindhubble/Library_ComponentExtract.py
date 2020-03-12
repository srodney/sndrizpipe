"""

DESCRIPTION:
    Trys to get a value from a python object by index
    On failure returns default value provided, or none

ARGS:

RETURNS:

"""

def Main(
    Object = None, 
    Key = None, 
    DefaultValue = None,
    CheckArguments = True,
    PrintExtra = False,
    ):

    if (CheckArguments):
        ArgumentErrorMessage = ""
        #if (Object is None):
        #    ArgumentErrorMessage += "(Object is None)\n"
        #if (Key is None):
        #    ArgumentErrorMessage += "(Key is None)\n"

        #if (DefaultValue is None):
        #    ArgumentErrorMessage += "(DefaultValue is None)\n"

        if (len(ArgumentErrorMessage) > 0 ):
            if(PrintExtra):
                print("ArgumentErrorMessage:\n", ArgumentErrorMessage)
            raise Exception(ArgumentErrorMessage)

    Result = DefaultValue

    try:
        Result = Object[Key]
    except:
        pass
    return Result
