"""
SOURCE:
    Mind of Douglas Adams
DESCRIPTION:
    Search a ProductListMetaData object for information.
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
    ProductListMetaData
        Type:
            <class 'NoneType'>
        Description:
            None
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
import json
import Library_ComponentExtract
#-------------------------------------------------------------------------------
def Main(
    ProductListMetaData= None,
    ProductListMetaDataFilePath = None,
    ConditionDictionary= None,
    CheckArguments = True,
    PrintExtra = False,
    ):

    Result = None

    if ProductListMetaData is None and ProductListMetaDataFilePath is not None:
        with open(ProductListMetaDataFilePath) as FileHandleObject:
            ProductListMetaData = json.load(FileHandleObject)


    if (CheckArguments):
        ArgumentErrorMessage = ""

        if (len(ArgumentErrorMessage) > 0 ):
            if(PrintExtra):
                print("ArgumentErrorMessage:\n", ArgumentErrorMessage)
            raise Exception(ArgumentErrorMessage)

    #print ('ProductListMetaData')
    #print (ProductListMetaData)

    PossibleItems = []
    for Item in ProductListMetaData:
        for Key, RequiredValue in ConditionDictionary.items():
            Value = Library_ComponentExtract.Main(
                Object          = Item,
                Key             = Key,
                DefaultValue    = None,  
                )
            Value = str(Value) 
            if Value == RequiredValue:
                PossibleItems.append( Item )
            
    Result = PossibleItems
    return Result 




























