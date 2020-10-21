"""
SOURCE:
    Mind of Douglas Adams
DESCRIPTION:
    Stip ALL the extensions from ALL the files.
    For Example:
        text.txt.py  --> text
        text.txt --> text
        text --> text
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
    ArrayOfStringFileNames
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
    ArrayOfStringFileNames= None,
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


    NoExtensionFileNames = []
    for FileName in ArrayOfStringFileNames:
        FileNamePieces = FileName.split(".")
        FileNamePiecesCount = len(FileNamePieces)
        NoExtensionFileName = FileNamePieces[-1]
        if FileNamePiecesCount > 1:
            NoExtensionFileName = FileNamePieces[0]

        NoExtensionFileNames.append(NoExtensionFileName)


    Result = NoExtensionFileNames
    return Result 












