"""
SOURCE:
    Mind of Douglas Adams
DESCRIPTION:
    Starts with a nested object. 
    Turns all the numpy elements inside the nested object,
    into lists by doing the \"to_list()\" method on them recursively
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
    NestedObject
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
    NestedObject= None,
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

    #For every kind of iterable object, check elements for numpy and cast them to python
    if isinstance(NestedObject, dict): 
        for key, value in NestedObject.items():
            #print ('key', key)
            #print ('value', value)

            if type(value).__module__ == 'numpy':
                value = value.tolist()
            else:
                value = Main( value )

            NestedObject[key] = value
    elif isinstance(NestedObject, list ):
        for item, index in zip(NestedObject, range(len(NestedObject)) ):
            NestedObject[index] = Main(item)

    elif type(NestedObject).__module__ == 'numpy':
        NestedObject = NestedObject.item()

    Result = NestedObject
    return Result 





























