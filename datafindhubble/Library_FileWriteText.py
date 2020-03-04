"""
SOURCE:

DESCRIPTION:

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


RETURNS:
    True if successfully wrote new infomration to a a file
    False if did not actually write anything to a file

"""
import Library_StringFilePathGetDirectory
import Library_FilePathExists
import Library_SystemDirectoryCreateSafe
 

def Main(
    Filepath = None,
    FilePath = None,
    WriteText = None,
    Text = None,
    OverWrite = False,
    CreateDirectoryIfNotExists = True,
    CheckArguments = True,
    PrintExtra = True,
    ):

    Result = False

    if (CheckArguments):
        ArgumentErrorMessage = ""

        if (Filepath is None and FilePath is None):
            ArgumentErrorMessage += 'No filepath provided'

        if (WriteText is None and Text is None):
            ArgumentErrorMessage += 'No text to write provided'


        if (len(ArgumentErrorMessage) > 0 ):
            if(PrintExtra):
                print("ArgumentErrorMessage:\n", ArgumentErrorMessage)
            raise Exception(ArgumentErrorMessage)


    #The arg handling who's who redudant arg names
    if (Filepath is None and FilePath is not None):
        Filepath = FilePath
    if (WriteText is None and Text is not None):
        WriteText = Text


    #Create the directory for the file to go into if it does not exist
    if CreateDirectoryIfNotExists:
        Directory = Library_StringFilePathGetDirectory.Main( FilePath = Filepath)
        Library_SystemDirectoryCreateSafe.Main( Directory = Directory )


    #Check if the file we want to write already exists and deterimine if we should overwrite it
    FilePathExists = Library_FilePathExists.Main(Filepath)
    ShouldWriteFile = False
    ShouldWriteFile = (not FilePathExists) or OverWrite


    #Actually write the contents to the file
    if (ShouldWriteFile):
        FileHandle = open(Filepath, 'w')
        FileHandle.write(WriteText)
        FileHandle.close()
        Result = True

    return Result 

























