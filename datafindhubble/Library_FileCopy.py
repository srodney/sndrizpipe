"""
SOURCE:
    Mind of Douglas Adams
DESCRIPTION:
    Copy a file from one path,
    to a different folder
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
    SourceFilePath
        Type:
            <class 'NoneType'>
        Description:
            None
    TargetFolderPath
        Type:
            <class 'NoneType'>
        Description:
            None
    Overwrite
        Type:
            <class 'NoneType'>
        Description:
            None
RETURNS:
    Result
        Type:
        Description:
"""

import shutil
import Library_StringFilePathGetFileName
import Library_SystemDirectoryCreateSafe
#-------------------------------------------------------------------------------
def Main(
    SourceFilePath= None,
    TargetFolderPath= None,
    Overwrite= None,
    CheckArguments = True,
    PrintExtra = False,
    ):

    Result = None

    if Overwrite is None:
        Overwrite = True

    if (CheckArguments):
        ArgumentErrorMessage = ""

        if (len(ArgumentErrorMessage) > 0 ):
            if(PrintExtra):
                print("ArgumentErrorMessage:\n", ArgumentErrorMessage)
            raise Exception(ArgumentErrorMessage)

    #Create the target folder if it does not exist:
    Library_SystemDirectoryCreateSafe.Main( Directory = TargetFolderPath )


    SourceFileName = Library_StringFilePathGetFileName.Main(SourceFilePath)
    if PrintExtra: print ('SourceFileName', SourceFileName)
    TargetFilePath = TargetFolderPath + '/' + SourceFileName
    if PrintExtra: print ('TargetFilePath', TargetFilePath)

    Result= shutil.copyfile( SourceFilePath, TargetFilePath )

    return Result 













