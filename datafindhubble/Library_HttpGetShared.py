"""
SOURCE:
    Mind of Douglas Adams
DESCRIPTION:
    Get the page source for a simple http request. 
    No bells and wistles.    
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
    Url
        Type:
            <class 'NoneType'>
        Description:
            None

    TimeOut
        Type:
            <class 'int'>
        Description:
            seconds

RETURNS:
    Result
        Type:
        Description:
"""
import requests
#-------------------------------------------------------------------------------
def Main(
    Url= None,
    TimeOut= None,
    CheckArguments = True,
    PrintExtra = False,
    ):

    Result = None

    if (TimeOut is None):
        TimeOut = 10


    if (CheckArguments):
        ArgumentErrorMessage = ""

        if (len(ArgumentErrorMessage) > 0 ):
            if(PrintExtra):
                print("ArgumentErrorMessage:\n", ArgumentErrorMessage)
            raise Exception(ArgumentErrorMessage)


    ResponseData = None

    ResponseObject = requests.get(
        Url, 
        proxies     = None, 
        auth        = None,
        timeout     = TimeOut,
        headers     = None,
        )
    ResponseData = ResponseObject.text.encode('utf-8')
    #ResponseData = ResponseObject.content.decode('utf-8')
    ResponseData = ResponseData.decode("utf-8") 

    Result = ResponseData

    return Result 
