"""
SOURCE:
    https://docs.scipy.org/doc/numpy/reference/generated/numpy.meshgrid.html

DESCRIPTION:
    Starting with a parentlist of childlists
    Generates a list of all possible combinations of choices
    Where exactly one element must be chosen from each childlist
    E.G.
        There are 3 bins of billiard balls
        Each bin's biliard balls, are numbered 1 - 9, 
        and each bin has balls of a single color (Bin1: yellow, Bin2: Green, Bin3: red)
        List all the possible balls you could have at the end:
        Yellow1, Green1, Red1
        Yellow2, Green1, Red1
        .
        Yellow9, Green9, Red9
        Total, there are 9*9*9 possibilities
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
            <type 'NoneType'>
        Description:
            A list of lists
RETURNS:
    Result
        Type:
        Description:
"""
import Library_DigitClock
def Main(
    ListOfLists= None,
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


    #TODO:
    #   numpy.meshgrid   on NUMBERS ONLY

    ListCount = len(ListOfLists)


    IndexMaximums = []
    for List in ListOfLists:
        IndexMaximums.append(len(List) - 1)
    #print 'IndexMaximums', IndexMaximums

    PossibilityIndexes = Library_DigitClock.Main( DigitMaximums = IndexMaximums )
    #print 'PossibilityIndexes', PossibilityIndexes

    Result = []
    for PossibilityIndex in PossibilityIndexes:
        Possibility = []
        for List, ListNumber in zip( ListOfLists, list(range(ListCount))):
            Choice = List[ PossibilityIndex[ListNumber] ]
            Possibility.append(Choice)
        #print 'Possibility', Possibility
        Result.append(Possibility)

    return Result 












