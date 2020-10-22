"""
SOURCE:
    Mind of Douglas Adams
DESCRIPTION:
    KNow the right directory to get metadata files
    Know which ones to load up.
    The only thing to pass in is the condition dictionary
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
    ConditionDictionary
        Type:
            <class 'NoneType'>
        Description:
            None
RETURNS:
    Result
        Type:
        Description:
"""
import pprint
import os
import glob
import Library_BarbaraMikulskiArchiveSearchProductListMetaData
import Library_SystemGetLocalDataDirectory
#-------------------------------------------------------------------------------
def Main(
    ConditionDictionary= None,
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


    DataDirectory = Library_SystemGetLocalDataDirectory.Main(    )
    SuperNovaMetaDataDirectory      = DataDirectory + '/AstronomySuperNovaData/SuperNovaHubbleMetaData/'

    SingleSuperNovaIdMetaDataSearchResults = []
    CatalogNames = ['pantheon', 'raisin', 'shoes']


    #Get the list of meta data files associated with all the catalogs we have:
    #   #(3 catalogs --> 3 json files ) [-4:-1]  gets the most recent
    #   FIXME: oof -> we need the most recent of EACH catalog... not possible duplicates
    #MetaDataFiles = sorted(os.listdir( SuperNovaMetaDataDirectory ))[-4:-1] 
    MetaDataFilePaths = []
    for CatalogName in CatalogNames:
        SingleCatalogAllMetaDataFilePaths = list( sorted( list(glob.iglob(SuperNovaMetaDataDirectory + '/**/*' + CatalogName + '.txt', recursive=True)) ) )
        MostRecentMetaDataFilePath = SingleCatalogAllMetaDataFilePaths[-1]
        #print ('MostRecentMetaDataFilePath', MostRecentMetaDataFilePath)
        MetaDataFilePaths.append(MostRecentMetaDataFilePath)
    print ('MetaDataFilePaths')
    pprint.pprint ( MetaDataFilePaths)


    #print ('MetaDataFilePaths', MetaDataFilePaths)

    for FilePath in MetaDataFilePaths:
        #FilePath = os.path.realpath( SuperNovaMetaDataDirectory + '/' + FileName )
        #print ('FilePath', FilePath)

        Result = Library_BarbaraMikulskiArchiveSearchProductListMetaData.Main(
            ProductListMetaDataFilePath = FilePath,
            ConditionDictionary= ConditionDictionary
            )
        #print( 'Search Result', Result ) 
        if not (Result in [None, []]):
            SingleSuperNovaIdMetaDataSearchResults.append(Result)

    Result = SingleSuperNovaIdMetaDataSearchResults

    return Result 





