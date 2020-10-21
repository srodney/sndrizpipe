"""
SOURCE:
    Mind of Douglas Adams
DESCRIPTION:
    Lazily dump an object to the local computer 
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
    Object
        Type:
            <class 'NoneType'>
        Description:
            None
RETURNS:
    Result
        Type:
        Description:
"""
import Library_FilePathExists
import Library_SystemGetLocalDataDirectory
import Library_DateStringNowGMT
import Library_PickleAndSaveToFile
import Library_SystemDirectoryCreateSafe
#-------------------------------------------------------------------------------
def Main(
    Object= None,
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

    #Where to save the pickle?
    DataDirectory = Library_SystemGetLocalDataDirectory.Main()
    LazyPickleDumpDirectory = DataDirectory + '/LazyPickleDump'
    Library_SystemDirectoryCreateSafe.Main( Directory = LazyPickleDumpDirectory )

    DateStringSave = Library_DateStringNowGMT.Main()
    StorageFilePath = LazyPickleDumpDirectory + '/' + DateStringSave + '.pkl'
    if PrintExtra: print ('DateStringSave (lazy pickle dump)', DateStringSave)
    if PrintExtra: print ('PickleDump StorageFilePath', StorageFilePath )
    #Do the save
    Library_PickleAndSaveToFile.Main(
        Object= Object,
        SaveFilePath= StorageFilePath,
        )

    #What to return?
    if Library_FilePathExists.Main( StorageFilePath ):
        Result = StorageFilePath
    else:
        Result = False
    return Result 



















