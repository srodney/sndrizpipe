"""
SOURCE:
    Mind of Douglas Adams
DESCRIPTION:
    A product list is downloaded into a directory:
        ProductListDownloadDirectory = \"/DataHome/AstronomySuperNovaData/SuperNovaHubbleImages/04D2al/mastDownload\"
    Astroquery creates subdirectories
        \"/mastDownload/HST/j8pu1cynq\"
        \"/mastDownload/HST/j8pu1cyrq\"
        \"/mastDownload/HST/j8pu1cyuq\"
        \"/mastDownload/HST/j8pu1cyyq\"
    Each subdirectory only has a single file.
    Recursively go through every directory in \"mastDownload\"
    and make a symlink to the actual datafiles within a new directory \"mastDownloadFilesSymlinks\"
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
    ProductListDownloadDirectory
        Type:
            <class 'NoneType'>
        Description:
            None
RETURNS:
    Result
        Type:
        Description:
"""
import glob
import os
import Library_StringFilePathGetFileName
import Library_SystemDirectoryCreateSafe
#-------------------------------------------------------------------------------
def Main(
    ProductListDownloadDirectory= None,
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
    #Safely create the download directory if it doesn't exist:
    Library_SystemDirectoryCreateSafe.Main(ProductListDownloadDirectory)


    #First we need to recursively find all the fits image files in the directory:
    #   https://stackoverflow.com/questions/2212643/python-recursive-folder-read
    FitsFilePaths = []
    for FilePath in glob.iglob(ProductListDownloadDirectory + '/**/*.fits', recursive=True):
        FitsFilePaths.append(FilePath)


    #Second we need to create a directory "neighboring" the product list directory 
    #   within which to put the flat files
    DownloadDirectoryName = Library_StringFilePathGetFileName.Main(ProductListDownloadDirectory)
    DownloadDirectoryNeighbor = os.path.dirname( ProductListDownloadDirectory ) + '/' + DownloadDirectoryName + 'FilesSymlinks.flt'
    DownloadDirectoryNeighbor = os.path.realpath(DownloadDirectoryNeighbor)
    Library_SystemDirectoryCreateSafe.Main(DownloadDirectoryNeighbor)



    #Third create the list of symlinks in the "neighbor" directory
    for FitsFilePath in FitsFilePaths:
        FitsFilePath = os.path.realpath(FitsFilePath)
        FitsFileName = Library_StringFilePathGetFileName.Main(FitsFilePath)
        SymlinkFilePath = DownloadDirectoryNeighbor + '/' + FitsFileName

        if PrintExtra:
            print ('SymlinkFilePath', SymlinkFilePath)
            print ('FitsFilePath   ', FitsFilePath)

        try:
            os.symlink(FitsFilePath, SymlinkFilePath  )
        #If the link already exists on the system - pass, and continue
        except FileExistsError:
            print ('SymlinkFilePath exists already')
        #If something else went wrong - raise the expection as normal
        except:
            raise

    Result = DownloadDirectoryNeighbor
    return Result 

















