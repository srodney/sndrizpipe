"""
SOURCE:
    Mind of Douglas Adams
DESCRIPTION:
    Goes to the open supernova catalog
    Obtains any information available based on search args
    Search args can be provided

    #Example_DataFindBarbaraMikulskiArchiveProductsHubbleSingleObject

    Example_DataFindOpenSuperNovaCatalogSingleObject

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
    SearchArgs
        Type:
            <class 'NoneType'>
        Description:
            None

    SuperNovaId
        Type:
            <class 'NoneType'>
        Description:
            None

RETURNS:
    Result
        Type:
        Description:
"""
import Library_HttpGetShared
import Library_JsonLoad
#-------------------------------------------------------------------------------
def Main(

    SuperNovaId = None,
    ResultFormat = None,
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

    #Example:
    #https://sne.space/astrocats/astrocats/supernovae/output/json/SNLS-03D1ax.json

    OpenSuperNovaCatalogId = "SNLS-" + SuperNovaId

    Url = "https://sne.space/astrocats/astrocats/supernovae/output/json/" + OpenSuperNovaCatalogId + ".json"
    SuperNovaDataJson = Library_HttpGetShared.Main(
        Url = Url,
        )
    SuperNovaDataNestedObject = Library_JsonLoad.Main(
        JsonString = SuperNovaDataJson,
        ForceAscii= True,
        )
    print ('SuperNovaDataNestedObject', SuperNovaDataNestedObject['SNLS-03D1ax'].keys())


    PhotometryUrl = "https://api.astrocats.space/" + OpenSuperNovaCatalogId + "/photometry/magnitude+e_magnitude+band+time"
    PhotometrySuperNovaDataJson = Library_HttpGetShared.Main(
        Url = PhotometryUrl,
        )    
    PhotometrySuperNovaDataNestedObject = Library_JsonLoad.Main(
        JsonString = PhotometrySuperNovaDataJson,
        ForceAscii= True,
        )
    print ('PhotometrySuperNovaDataNestedObject', PhotometrySuperNovaDataNestedObject['SNLS-03D1ax'].keys())

    if ResultFormat is None:
        Result = SuperNovaDataNestedObject
    elif ResultFormat == 'PhotometryOnly':
        Result = PhotometrySuperNovaDataNestedObject

    return Result 



















