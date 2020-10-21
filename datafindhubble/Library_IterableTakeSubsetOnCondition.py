"""
SOURCE:
    Mind of Douglas Adams
DESCRIPTION:
    Takes a subset of any iterable for which the condition is satisfied
    The conditionfunction must return true or false
    Returns every item for which the condition function returns true
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
    Iterable
        Type:
            <type 'NoneType'>
        Description:
    ConditionFunction
        Type:
            <type 'NoneType'>
        Description:
RETURNS:
    Result
        Type:
        Description:
"""
def Main(
    Iterable= None,
    ConditionFunction= None,
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

    Result = []
    for Item in Iterable:
        if ConditionFunction(Item):
            Result.append(Item)
    
    return Result 





