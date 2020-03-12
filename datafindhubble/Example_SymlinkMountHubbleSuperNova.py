
import Library_SystemGetLocalHomeDirectory
import socket
import os
import Library_BarbaraMikulskiArchiveSymlinkGroupMastDownloadDirectoryFiles
#-------------------------------------------------------------------------------
#Directory Management:
HomeDirectory = Library_SystemGetLocalHomeDirectory.Main()
DataDirectory = HomeDirectory + '/DataHome'

HostName = socket.gethostname()
print ('HostName:', HostName)
if HostName == 'login001':
    DataDirectory = '/work/da2/DataHome'
print ('DataDirectory:' , DataDirectory)

SuperNovaCatalogsDataDirectory  = DataDirectory + '/AstronomySuperNovaData/SuperNovaCatalogs/'
SuperNovaImageDownloadDirectory = DataDirectory + '/AstronomySuperNovaData/SuperNovaHubbleImages/'
SuperNovaMetaDataDirectory      = DataDirectory + '/AstronomySuperNovaData/SuperNovaHubbleMetaData/'
#-------------------------------------------------------------------------------


#Get the list of directories for which we downloaded supernova data:
SuperNovaHubbleImageDirectories = os.listdir(SuperNovaImageDownloadDirectory) 

#For each supernova, we should make symlinks to merge the fits files into one directory:
for FolderName in SuperNovaHubbleImageDirectories:
    ProductListDirectory = os.path.realpath( SuperNovaImageDownloadDirectory + '/' +  FolderName + '/mastDownload' )
    print ('ProductListDirectory', ProductListDirectory)

    ResultSymlinkDirectory = Library_BarbaraMikulskiArchiveSymlinkGroupMastDownloadDirectoryFiles.Main(
        ProductListDownloadDirectory= ProductListDirectory
        )
    print( 'Created symlink directory:', ResultSymlinkDirectory)


