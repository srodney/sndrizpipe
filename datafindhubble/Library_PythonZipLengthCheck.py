"""
SOURCE:
    Mind of Douglas Adams
DESCRIPTION:
    Check a list of lists to make sure they are all the same length
    if same lengths return true    
    if not return false
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
    ListOfLists
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
    ListOfLists= None,
    ListOfListNames = None,
    RaiseException = None,
    CheckArguments = True,
    PrintExtra = False,
    ):

    Result = None

    if RaiseException is None:
        RaiseException = False

    if ListOfListNames is None:
        ListOfListNames = ['NameNotProvided']*len(ListOfLists)

    if (CheckArguments):
        ArgumentErrorMessage = ""

        if (len(ArgumentErrorMessage) > 0 ):
            if(PrintExtra):
                print("ArgumentErrorMessage:\n", ArgumentErrorMessage)
            raise Exception(ArgumentErrorMessage)


    ListOfLengths = []
    for List in ListOfLists:
        ListOfLengths.append( len(List) )



    UniqueLengthCount = len(list(set(ListOfLengths)))

    if UniqueLengthCount == 1:
        Result = True
    elif UniqueLengthCount > 1:
        Result = False
    else:
        raise Exception ('`ListOfLists` is really bad. No lengths found')


    if Result == False and RaiseException:
        ExceptionMessage = "Each list in `ListOfLists` does not have same length.\n" 
        ExceptionMessage  += 'ListOfLengths: ' + str(ListOfLengths) + '\n'
        ExceptionMessage  += 'UniqueLengthCount: ' + str( UniqueLengthCount )
        #for List in ListOfLists:
        #    #ListName = varname.nameof(List)
        #    ListName = ''
        #    ExceptionMessage += 'len(' + ListName + ')==' 
        #    ExceptionMessage +=  str(len(List)) + '\n'
        
        raise Exception(ExceptionMessage)


    return Result 















