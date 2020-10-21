"""
SOURCE:
    Mind of Douglas Adams
DESCRIPTION:
    Goes and gets the local datahome directory. 
    This is machine dependent. 
    On clusters, the datahome directory will be different than on the local machine. 
    Inside docker containers, it might also change. 
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
    Result
        Type:
        Description:
"""
import os
import socket
import Library_SystemGetLocalHomeDirectory
import Library_SystemDirectoryCreateSafe
#import Library_SystemGetLocalDataDirectory

#-------------------------------------------------------------------------------
def Main(
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


    #If we are on a local machine, then fix the data directory to be in the home directory
    HomeDirectory = Library_SystemGetLocalHomeDirectory.Main()
    DataDirectory = HomeDirectory + '/DataHome'


    #If we are on the south carolina cluster, then choose doug adams data directory properly:
    HostName = socket.gethostname()
    if PrintExtra: print ('HostName:', HostName)
    if (HostName == 'login001') or ('node' in HostName):
        ClusterUser = os.getcwd().split('/')[2] #[da2, jr23, ... , etc]
        DataDirectory = '/work/' + ClusterUser +'/DataHome'
        Library_SystemDirectoryCreateSafe.Main( Directory = DataDirectory )

    Result = DataDirectory
    return Result 














