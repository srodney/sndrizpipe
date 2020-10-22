sys.path.insert(1, '../datafindhubble')

import Library_SystemGetLocalHomeDirectory

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


