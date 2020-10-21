"""
SOURCE:
    Mind of Douglas Adams
DESCRIPTION:
    Query a region of the open supernova catalog for supernova.
    Use .2 arc seconds by default.
    Will return a list of all the SN which are in the radius.
    (for all time)
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
    RightAscension
        Type:
            <class 'NoneType'>
        Description:
            None
    Declination
        Type:
            <class 'NoneType'>
        Description:
            None
    Radius
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
import astropy
import astropy.units
import astropy.coordinates

#-------------------------------------------------------------------------------
def Main(
    RightAscension= None,
    Declination= None,
    Radius= None, #In arc seconds
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

    
    #Convert the degrees to the min, sec, arcsec
    AstropySkyCoordinateObject = astropy.coordinates.SkyCoord(
        ra = RightAscension * astropy.units.degree, 
        dec = Declination* astropy.units.degree, 
        frame='icrs',  #Double check this
        unit='deg',
        )
    
    TimeCoordinates = AstropySkyCoordinateObject.to_string('hmsdms')
    print ('TimeCoordinates', TimeCoordinates)
    #RaTimeCoords = TimeCoordinates[0]
    #DecTimeCoords = TimeCoordinates[1]

    #RaTimeCoords = str(RightAscension)
    #DecTimeCoords = str(Declination)


    Ra_hh = TimeCoordinates.split(' ')[0].split('h')[0]
    print ('Ra_hh', Ra_hh)
    Ra_mm = TimeCoordinates.split(' ')[0].split('m')[0].split('h')[1]
    print ('Ra_mm', Ra_mm)
    Ra_ss = TimeCoordinates.split(' ')[0].split('s')[0].split('m')[1]
    print ('Ra_ss', Ra_ss)
    RaTimeCoords = Ra_hh + ':' + Ra_mm + ':' + Ra_ss
    print ('RaTimeCoords', RaTimeCoords)



    Dec_dd = TimeCoordinates.split(' ')[1].split('d')[0]
    print ('Dec_dd', Dec_dd)
    Dec_mm = TimeCoordinates.split(' ')[1].split('m')[0].split('d')[1]
    print ('Dec_mm', Dec_mm)
    Dec_ss = TimeCoordinates.split(' ')[1].split('s')[0].split('m')[1]
    print ('Dec_ss', Dec_ss)
    DecTimeCoords = Dec_dd + ':' + Dec_mm + ':' + Dec_ss
    print ('DecTimeCoords', DecTimeCoords)




    #Example Data Search:
    # https://api.astrocats.space/catalog?ra=21:23:32.16&dec=-53:01:36.08&radius=2
    Url = "https://api.astrocats.space/catalog?ra=" + RaTimeCoords +"&dec="+DecTimeCoords+"&radius=" + str(Radius)
    SuperNovaDataJson = Library_HttpGetShared.Main(
        Url = Url,
        )
    SuperNovaDataNestedObject = Library_JsonLoad.Main(
        JsonString = SuperNovaDataJson,
        ForceAscii= True,
        )

    Result = SuperNovaDataNestedObject

    return Result 


























